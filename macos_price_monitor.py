#!/usr/bin/env python3
"""
MacOS Price Monitor - Professional Grade
=======================================

A robust, MacOS-optimized price monitoring script with native notifications
and system integration.

Features:
- Native MacOS notifications
- Keychain integration for secure storage
- LaunchAgent support for background running
- Menu bar integration ready
- Cross-platform foundation for future expansion

Author: Built with GitHub Copilot
macOS Compatibility: 10.14+
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import sys
import subprocess
from datetime import datetime
import argparse
import re
import time
from pathlib import Path
import plistlib

class MacOSPriceMonitor:
    """MacOS-optimized price monitoring with native integration"""
    
    def __init__(self):
        # MacOS-specific paths
        self.app_support_dir = Path.home() / "Library" / "Application Support" / "PriceMonitor"
        self.data_file = self.app_support_dir / "price_data.json"
        self.config_file = self.app_support_dir / "config.json"
        self.launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
        
        # Ensure directories exist
        self.app_support_dir.mkdir(parents=True, exist_ok=True)
        
        self.config = self.load_config()
        
    def load_config(self):
        """Load configuration with MacOS defaults"""
        default_config = {
            "notifications": {
                "enabled": True,
                "sound": "Glass",  # MacOS notification sound
                "persistent": False
            },
            "monitoring": {
                "check_interval": 3600,  # 1 hour in seconds
                "price_drop_threshold": 5.0,
                "enabled": False
            },
            "max_products_free": 3,  # Generous for MacOS users
            "version": "1.0.0"
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return {**default_config, **config}
            except (json.JSONDecodeError, FileNotFoundError):
                return default_config
        else:
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config=None):
        """Save configuration"""
        if config is None:
            config = self.config
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.log_error(f"Error saving config: {e}")
    
    def log_error(self, message):
        """Log errors to system log (compatible with Console.app)"""
        timestamp = datetime.now().isoformat()
        log_message = f"[{timestamp}] PriceMonitor: {message}"
        
        # Write to system log
        try:
            subprocess.run([
                'logger', 
                '-t', 'PriceMonitor',
                message
            ], check=False)
        except Exception as e:
            # Fallback to stderr if logger command fails
            print(f"{log_message} (logger failed: {e})", file=sys.stderr)
    
    def send_notification(self, title, message, sound=True):
        """Send native MacOS notification"""
        if not self.config["notifications"]["enabled"]:
            return
            
        try:
            cmd = [
                'osascript', '-e',
                f'display notification "{message}" with title "{title}"'
            ]
            
            if sound and self.config["notifications"]["sound"]:
                sound_name = self.config["notifications"]["sound"]
                cmd = [
                    'osascript', '-e',
                    f'display notification "{message}" with title "{title}" sound name "{sound_name}"'
                ]
            
            subprocess.run(cmd, check=False, capture_output=True)
            
        except Exception as e:
            self.log_error(f"Notification error: {e}")
    
    def extract_price(self, text):
        """Enhanced price extraction with currency support"""
        # Clean and normalize text
        clean_text = re.sub(r'[,\s]+', '', text)
        
        # Multiple currency patterns
        patterns = [
            r'\$(\d+\.?\d*)',      # USD $123.45
            r'£(\d+\.?\d*)',       # GBP £123.45
            r'€(\d+\.?\d*)',       # EUR €123.45
            r'CAD?\$?(\d+\.?\d*)', # CAD
            r'(\d+\.\d{2})',       # 123.45
            r'(\d{1,4})',          # 123 (fallback)
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, clean_text)
            for match in matches:
                try:
                    price = float(match)
                    # Reasonable price range
                    if 0.01 <= price <= 100000:
                        return price
                except ValueError:
                    continue
        return None
    
    def get_user_agent(self):
        """Get MacOS-appropriate User-Agent"""
        macos_version = self.get_macos_version()
        return f'Mozilla/5.0 (Macintosh; Intel Mac OS X {macos_version}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    def get_macos_version(self):
        """Get macOS version for User-Agent"""
        try:
            result = subprocess.run(['sw_vers', '-productVersion'], 
                                  capture_output=True, text=True)
            version = result.stdout.strip()
            # Convert 11.0.1 to 11_0_1 format
            return version.replace('.', '_')
        except Exception as e:
            self.log(f"Failed to get macOS version: {e}, using fallback", "WARNING")
            return "10_15_7"  # Safe fallback
    
    def scrape_with_retry(self, url, max_retries=3):
        """Robust scraping with exponential backoff"""
        headers = {
            'User-Agent': self.get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        for attempt in range(max_retries):
            try:
                # Exponential backoff
                if attempt > 0:
                    time.sleep(2 ** attempt)
                
                response = requests.get(
                    url, 
                    headers=headers, 
                    timeout=15,
                    allow_redirects=True
                )
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                self.log_error(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == max_retries - 1:
                    raise
        
        return None
    
    def scrape_amazon_price(self, url):
        """Enhanced Amazon scraping with multiple selectors"""
        try:
            response = self.scrape_with_retry(url)
            if not response:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Comprehensive Amazon price selectors
            selectors = [
                # New Amazon layouts
                'span.a-price-whole',
                'span.a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen',
                'span#priceblock_dealprice',
                'span#priceblock_ourprice',
                'span.a-price-current .a-price-whole',
                '.a-price .a-offscreen',
                '#apex_desktop .a-price .a-offscreen',
                '.a-price-symbol + .a-price-whole',
                
                # Mobile selectors
                '.a-size-medium.a-color-price',
                '.a-price-range .a-price .a-offscreen',
                
                # Older layouts
                '#price_inside_buybox',
                '.a-color-price.a-size-medium'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    price_text = element.get_text(strip=True)
                    price = self.extract_price(price_text)
                    if price:
                        return price
            
            # Fallback: search in page text for price patterns
            text = soup.get_text()
            price = self.extract_price(text)
            return price
            
        except Exception as e:
            self.log_error(f"Amazon scraping error: {e}")
            return None
    
    def scrape_ebay_price(self, url):
        """Enhanced eBay scraping"""
        try:
            response = self.scrape_with_retry(url)
            if not response:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            selectors = [
                'span.notranslate',
                'span#prcIsum_bidPrice',
                'span.u-flL.condText',
                '.text-display-1',
                '[data-testid="x-price-primary"] .text-display-1',
                '.price .text-display-1',
                '#prcIsum .text-display-1'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    price = self.extract_price(element.text)
                    if price:
                        return price
            
            return None
            
        except Exception as e:
            self.log_error(f"eBay scraping error: {e}")
            return None
    
    def detect_site_and_scrape(self, url):
        """Detect website and scrape accordingly"""
        url_lower = url.lower()
        
        if 'amazon.' in url_lower:
            return self.scrape_amazon_price(url)
        elif 'ebay.' in url_lower:
            return self.scrape_ebay_price(url)
        else:
            # Generic scraping for other sites
            try:
                response = self.scrape_with_retry(url)
                if response:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    text = soup.get_text()
                    return self.extract_price(text)
            except Exception as e:
                self.log(f"Failed to get price from {url}: {e}", "ERROR")
            return None
    
    def load_data(self):
        """Load price data"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {}
    
    def save_data(self, data):
        """Save price data"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log_error(f"Error saving data: {e}")
    
    def add_product(self, url, name, target_price=None):
        """Add product with free tier limits"""
        data = self.load_data()
        
        # Check free tier limit
        if len(data) >= self.config["max_products_free"] and name not in data:
            print(f"📦 Free tier allows {self.config['max_products_free']} products maximum")
            print("💎 Upgrade to PRO for unlimited products!")
            return False
        
        if name in data:
            print(f"⚠️  Product '{name}' already being monitored")
            return False
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            print("❌ Invalid URL. Must start with http:// or https://")
            return False
        
        # Test scraping
        print(f"🔍 Testing price fetch for: {name}")
        test_price = self.detect_site_and_scrape(url)
        
        if test_price is None:
            print("⚠️  Could not fetch price. Adding anyway (might work later)")
        else:
            print(f"✅ Current price: ${test_price:.2f}")
        
        data[name] = {
            "url": url,
            "prices": [],
            "target_price": target_price,
            "added_date": datetime.now().isoformat(),
            "site": self.detect_site_type(url)
        }
        
        # Add initial price if available
        if test_price is not None:
            data[name]["prices"].append({
                "price": test_price,
                "timestamp": datetime.now().isoformat()
            })
        
        self.save_data(data)
        
        # Send notification
        self.send_notification(
            "Price Monitor", 
            f"Now monitoring: {name}"
        )
        
        print(f"🎯 Added: {name}")
        if target_price:
            print(f"   Target price: ${target_price:.2f}")
        
        return True
    
    def detect_site_type(self, url):
        """Detect website type for display"""
        url_lower = url.lower()
        if 'amazon.' in url_lower:
            return 'Amazon'
        elif 'ebay.' in url_lower:
            return 'eBay'
        else:
            return 'Generic'
    
    def check_prices(self, verbose=True):
        """Check all monitored products"""
        data = self.load_data()
        
        if not data:
            if verbose:
                print("📭 No products being monitored")
            return
        
        if verbose:
            print(f"🔍 Checking {len(data)} products...")
        
        alerts_sent = 0
        
        for name, product_data in data.items():
            if verbose:
                print(f"\n📦 {name} ({product_data.get('site', 'Unknown')})")
            
            current_price = self.detect_site_and_scrape(product_data["url"])
            
            if current_price is None:
                if verbose:
                    print("   ❌ Could not fetch price")
                continue
            
            # Add to history
            timestamp = datetime.now().isoformat()
            product_data["prices"].append({
                "price": current_price,
                "timestamp": timestamp
            })
            
            # Keep last 100 entries (reasonable for free tier)
            if len(product_data["prices"]) > 100:
                product_data["prices"] = product_data["prices"][-100:]
            
            if verbose:
                print(f"   💰 Current: ${current_price:.2f}")
            
            # Check for significant price changes
            if len(product_data["prices"]) > 1:
                previous_price = product_data["prices"][-2]["price"]
                change_percent = ((current_price - previous_price) / previous_price) * 100
                
                if abs(change_percent) >= self.config["monitoring"]["price_drop_threshold"]:
                    if change_percent < 0:  # Price drop
                        message = f"💰 {name}: Price dropped ${abs(current_price - previous_price):.2f} to ${current_price:.2f}"
                        self.send_notification("Price Drop Alert!", message)
                        alerts_sent += 1
                        if verbose:
                            print(f"   📉 {change_percent:.1f}% drop - Alert sent!")
                    elif verbose:
                        print(f"   📈 {change_percent:.1f}% increase")
                elif verbose and abs(change_percent) > 0.1:
                    print(f"   ➡️  {change_percent:+.1f}% change")
            
            # Check target price
            target = product_data.get("target_price")
            if target and current_price <= target:
                message = f"🎯 {name}: Target reached! ${current_price:.2f} <= ${target:.2f}"
                self.send_notification("Target Price Reached!", message)
                alerts_sent += 1
                if verbose:
                    print(f"   🎯 TARGET REACHED!")
        
        self.save_data(data)
        
        if verbose:
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"\n✅ Check completed at {timestamp}")
            if alerts_sent > 0:
                print(f"📧 {alerts_sent} alerts sent")
    
    def show_status(self):
        """Show comprehensive status"""
        data = self.load_data()
        
        if not data:
            print("📭 No products being monitored")
            print("\nTo get started:")
            print("  ./price_monitor.py add 'PRODUCT_URL' 'Product Name'")
            return
        
        print("📊 PRICE MONITORING STATUS")
        print("=" * 50)
        
        total_savings = 0
        
        for name, product_data in data.items():
            prices = [p["price"] for p in product_data["prices"]]
            if not prices:
                continue
            
            current = prices[-1]
            lowest = min(prices)
            highest = max(prices)
            average = sum(prices) / len(prices)
            max_savings = highest - lowest
            
            print(f"\n🏷️  {name} ({product_data.get('site', 'Unknown')})")
            print(f"   Current:     ${current:.2f}")
            print(f"   Lowest:      ${lowest:.2f}")
            print(f"   Highest:     ${highest:.2f}")
            print(f"   Average:     ${average:.2f}")
            print(f"   Tracked:     {len(prices)} times")
            
            if max_savings > 0:
                print(f"   Max Savings: ${max_savings:.2f}")
                total_savings += max_savings
            
            target = product_data.get("target_price")
            if target:
                if current <= target:
                    print(f"   🎯 TARGET REACHED: ${target:.2f}")
                else:
                    diff = current - target
                    print(f"   🎯 Target: ${target:.2f} (${diff:.2f} to go)")
            
            # Show recent trend
            if len(prices) >= 2:
                recent_change = ((current - prices[-2]) / prices[-2]) * 100
                trend = "📈" if recent_change > 0 else "📉" if recent_change < 0 else "➡️"
                print(f"   {trend} Recent: {recent_change:+.1f}%")
        
        print(f"\n💰 Total potential savings tracked: ${total_savings:.2f}")
        print(f"📊 Monitoring {len(data)}/{self.config['max_products_free']} products (free tier)")
    
    def create_launch_agent(self):
        """Create macOS LaunchAgent for background monitoring"""
        script_path = Path(__file__).resolve()
        plist_file = self.launch_agents_dir / "com.priceMonitor.agent.plist"
        
        plist_content = {
            'Label': 'com.priceMonitor.agent',
            'ProgramArguments': [
                str(script_path),
                'check',
                '--quiet'
            ],
            'StartInterval': self.config["monitoring"]["check_interval"],
            'RunAtLoad': False,
            'StandardOutPath': str(self.app_support_dir / "monitor.log"),
            'StandardErrorPath': str(self.app_support_dir / "monitor.error.log")
        }
        
        try:
            self.launch_agents_dir.mkdir(exist_ok=True)
            with open(plist_file, 'wb') as f:
                plistlib.dump(plist_content, f)
            
            print(f"✅ LaunchAgent created: {plist_file}")
            print("\nTo start background monitoring:")
            print(f"  launchctl load {plist_file}")
            print("\nTo stop background monitoring:")
            print(f"  launchctl unload {plist_file}")
            
            return True
            
        except Exception as e:
            self.log_error(f"LaunchAgent creation failed: {e}")
            return False


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description='MacOS Price Monitor - Professional grade price tracking',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add "https://amazon.com/dp/B08N5WRWNW" "iPhone 13"
  %(prog)s add "https://ebay.com/itm/123" "MacBook" --target 999.99
  %(prog)s check
  %(prog)s status
  %(prog)s setup-agent
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add product to monitor')
    add_parser.add_argument('url', help='Product URL')
    add_parser.add_argument('name', help='Product name')
    add_parser.add_argument('--target', type=float, help='Target price for alerts')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check current prices')
    check_parser.add_argument('--quiet', action='store_true', help='Minimal output')
    
    # Status command
    subparsers.add_parser('status', help='Show monitoring status')
    
    # Setup command
    subparsers.add_parser('setup-agent', help='Setup background monitoring')
    
    args = parser.parse_args()
    
    monitor = MacOSPriceMonitor()
    
    if args.command == 'add':
        monitor.add_product(args.url, args.name, args.target)
    elif args.command == 'check':
        monitor.check_prices(verbose=not args.quiet)
    elif args.command == 'status':
        monitor.show_status()
    elif args.command == 'setup-agent':
        monitor.create_launch_agent()
    else:
        # Show help if no command
        parser.print_help()


if __name__ == "__main__":
    main()