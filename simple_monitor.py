#!/usr/bin/env python3
"""
Price Monitor Scraper - Simple Version
=====================================

A simple but effective tool for monitoring product prices.
This is the FREE version - upgrade to PRO for unlimited products!

Features:
- Monitor 1 product (FREE) / Unlimited (PRO)
- Amazon & eBay support
- Price history tracking
- Email alerts (PRO only)
- Simple command-line interface

Usage:
    python simple_monitor.py --url "https://amazon.com/product" --name "Product Name"

"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import argparse
import re
import time

class SimplePriceMonitor:
    """Simple Price Monitor - Free Version"""
    
    def __init__(self):
        self.data_file = "price_data.json"
        self.max_products = 1  # FREE version limit
        
    def extract_price(self, text):
        """Extract price from text"""
        # Remove common symbols and spaces
        clean_text = text.replace(',', '').replace(' ', '')
        
        # Find price patterns
        patterns = [
            r'\$(\d+\.?\d*)',  # $123.45
            r'(\d+\.\d{2})',   # 123.45
            r'(\d+)',          # 123
        ]
        
        for pattern in patterns:
            match = re.search(pattern, clean_text)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, IndexError):
                    continue
        return None
    
    def scrape_amazon(self, url):
        """Scrape Amazon product price"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple price selectors
            selectors = [
                'span.a-price-whole',
                'span#priceblock_dealprice',
                'span#priceblock_ourprice',
                'span.a-price.a-text-price.a-size-medium.apexPriceToPay',
                'span.a-price-current'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    price = self.extract_price(element.text)
                    if price:
                        return price
            
            # Fallback: search in page text
            text = soup.get_text()
            lines = text.split('\n')
            for line in lines:
                if '$' in line and len(line) < 50:  # Short lines more likely to contain price
                    price = self.extract_price(line)
                    if price and 1 < price < 10000:  # Reasonable price range
                        return price
                        
        except Exception as e:
            print(f"Error scraping Amazon: {e}")
        
        return None
    
    def scrape_ebay(self, url):
        """Scrape eBay product price"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # eBay price selectors
            selectors = [
                'span.notranslate',
                'span#prcIsum_bidPrice',
                'span.u-flL.condText',
                'div[data-testid="x-price-primary"]'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    price = self.extract_price(element.text)
                    if price:
                        return price
                        
        except Exception as e:
            print(f"Error scraping eBay: {e}")
        
        return None
    
    def get_price(self, url):
        """Get price from URL"""
        if 'amazon.' in url:
            return self.scrape_amazon(url)
        elif 'ebay.' in url:
            return self.scrape_ebay(url)
        else:
            print("Unsupported website. Supports: Amazon, eBay")
            return None
    
    def load_data(self):
        """Load existing price data"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON in data file: {e}")
                return {}
            except Exception as e:
                print(f"Warning: Failed to load data file: {e}")
                return {}
        return {}
    
    def save_data(self, data):
        """Save price data"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def monitor_product(self, url, name):
        """Monitor a single product"""
        data = self.load_data()
        
        # FREE version: limit to 1 product
        if len(data) >= self.max_products and name not in data:
            print("🔒 FREE VERSION LIMIT: You can only monitor 1 product.")
            print("💎 Upgrade to PRO for unlimited products!")
            print("   - Unlimited product monitoring")
            print("   - Email notifications")
            print("   - Price history charts")
            print("   - Automated scheduling")
            return
        
        print(f"🔍 Checking price for: {name}")
        
        current_price = self.get_price(url)
        
        if current_price is None:
            print("❌ Could not fetch price. Please check the URL.")
            return
        
        timestamp = datetime.now().isoformat()
        
        # Initialize product data
        if name not in data:
            data[name] = {
                "url": url,
                "prices": []
            }
        
        # Add current price
        data[name]["prices"].append({
            "price": current_price,
            "timestamp": timestamp
        })
        
        # Keep only last 10 price points (FREE version limit)
        if len(data[name]["prices"]) > 10:
            data[name]["prices"] = data[name]["prices"][-10:]
        
        self.save_data(data)
        
        # Display results
        print(f"💰 Current price: ${current_price:.2f}")
        
        if len(data[name]["prices"]) > 1:
            previous_price = data[name]["prices"][-2]["price"]
            change = current_price - previous_price
            change_percent = (change / previous_price) * 100
            
            if change > 0:
                print(f"📈 Price increased by ${change:.2f} ({change_percent:+.1f}%)")
            elif change < 0:
                print(f"📉 Price dropped by ${abs(change):.2f} ({change_percent:.1f}%)")
            else:
                print("➡️  Price unchanged")
        
        # Show mini history
        print("\n📊 Recent price history:")
        for entry in data[name]["prices"][-5:]:  # Show last 5
            date = datetime.fromisoformat(entry["timestamp"]).strftime("%m/%d %H:%M")
            print(f"   {date}: ${entry['price']:.2f}")
    
    def show_stats(self):
        """Show statistics for monitored products"""
        data = self.load_data()
        
        if not data:
            print("No products being monitored yet.")
            print("Usage: python simple_monitor.py --url 'PRODUCT_URL' --name 'PRODUCT_NAME'")
            return
        
        print("📊 MONITORING STATISTICS")
        print("=" * 40)
        
        for name, product_data in data.items():
            prices = [p["price"] for p in product_data["prices"]]
            if prices:
                current = prices[-1]
                lowest = min(prices)
                highest = max(prices)
                average = sum(prices) / len(prices)
                
                print(f"\n🏷️  {name}")
                print(f"   Current:  ${current:.2f}")
                print(f"   Lowest:   ${lowest:.2f}")
                print(f"   Highest:  ${highest:.2f}")
                print(f"   Average:  ${average:.2f}")
                print(f"   Tracked:  {len(prices)} times")


def main():
    parser = argparse.ArgumentParser(description='Simple Price Monitor - FREE Version')
    parser.add_argument('--url', help='Product URL to monitor')
    parser.add_argument('--name', help='Product name for tracking')
    parser.add_argument('--stats', action='store_true', help='Show monitoring statistics')
    
    args = parser.parse_args()
    
    monitor = SimplePriceMonitor()
    
    if args.stats:
        monitor.show_stats()
    elif args.url and args.name:
        monitor.monitor_product(args.url, args.name)
    else:
        print("🛒 Simple Price Monitor - FREE Version")
        print("\nUsage:")
        print("  python simple_monitor.py --url 'PRODUCT_URL' --name 'PRODUCT_NAME'")
        print("  python simple_monitor.py --stats")
        print("\nExample:")
        print("  python simple_monitor.py --url 'https://amazon.com/dp/B08N5WRWNW' --name 'iPhone 13'")
        print("\n💎 Want more features? Upgrade to PRO version!")
        print("   ✅ Unlimited products")
        print("   ✅ Email notifications") 
        print("   ✅ Automated scheduling")
        print("   ✅ Price charts & analytics")

if __name__ == "__main__":
    main()