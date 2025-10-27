"""
Price Monitor Scraper - Professional Edition
============================================

A powerful tool for monitoring product prices across major e-commerce platforms.

Features:
- Amazon price tracking
- eBay price monitoring  
- Email notifications
- Price history tracking
- Multiple product support
- Automated scheduling

Author: Your Name
License: Commercial
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
import json
import os
from datetime import datetime, timedelta
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import click
from colorama import Fore, Style, init
from dotenv import load_dotenv
import re
import random
import urllib.parse
import platform
import shutil
import subprocess
from pathlib import Path

# Initialize colorama for colored console output
init(autoreset=True)

# Load environment variables
load_dotenv()

class PriceMonitor:
    """Professional Price Monitoring System"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.data_file = "price_history.json"
        self.setup_logging()
        self.config = self.load_config()
        self.setup_driver()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('price_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self):
        """Setup Chrome driver for JavaScript-heavy sites"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.info("Chrome driver initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome driver: {e}")
            self.driver = None
    
    def load_config(self):
        """Load configuration from JSON file"""
        default_config = {
            "products": [],
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "",
                "sender_password": "",
                "recipient_email": ""
            },
            "check_interval": 60,  # minutes
            "price_drop_threshold": 5  # percentage
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
                return default_config
        else:
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config=None):
        """Save configuration to JSON file"""
        if config is None:
            config = self.config
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            self.logger.info("Configuration saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")

    def play_notification_sound(self):
        """Play a short notification sound in a cross-platform manner"""
        try:
            system = platform.system()

            if system == 'Darwin':
                sound_file = Path('/System/Library/Sounds/Glass.aiff')
                if shutil.which('afplay') and sound_file.exists():
                    subprocess.run(['afplay', str(sound_file)], check=False)
                else:
                    self._terminal_beep()
            elif system == 'Windows':
                try:
                    import winsound  # type: ignore
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                except Exception:
                    self._terminal_beep()
            else:
                # Attempt Linux/Unix players in order of preference
                sound_path_candidates = [
                    Path('/usr/share/sounds/freedesktop/stereo/complete.oga'),
                    Path('/usr/share/sounds/freedesktop/stereo/message.oga'),
                    Path('/usr/share/sounds/alsa/Front_Center.wav'),
                ]
                player = 'paplay' if shutil.which('paplay') else 'aplay' if shutil.which('aplay') else None

                if player:
                    for candidate in sound_path_candidates:
                        if candidate.exists():
                            subprocess.run([player, str(candidate)], check=False)
                            break
                    else:
                        self._terminal_beep()
                else:
                    self._terminal_beep()
        except Exception as sound_error:
            self.logger.debug(f"Notification sound failed: {sound_error}")
            self._terminal_beep()

    def _terminal_beep(self):
        """Fallback terminal bell"""
        print('\a', end='')

    def notify_completion(self, message: str):
        """Log, print, and chime when a task completes"""
        self.logger.info(message)
        print(f"{Fore.MAGENTA}🔔 {message}{Style.RESET_ALL}")
        self.play_notification_sound()
        self.show_macos_notification("Price Monitor", message)

    def show_macos_notification(self, title: str, body: str):
        """Trigger a macOS notification with optional sound"""
        if platform.system() != 'Darwin':
            return

        try:
            # Escape quotes safely for AppleScript
            script = f'display notification {json.dumps(body)} with title {json.dumps(title)} sound name "Glass"'
            subprocess.run(['osascript', '-e', script], check=False)
        except Exception as notify_error:
            self.logger.debug(f"macOS notification failed: {notify_error}")
    
    def extract_price_from_text(self, text):
        """Extract price from text using regex"""
        # Common price patterns
        patterns = [
            r'\$[\d,]+\.?\d*',  # $123.45, $1,234
            r'£[\d,]+\.?\d*',   # £123.45
            r'€[\d,]+\.?\d*',   # €123.45
            r'[\d,]+\.?\d*',    # 123.45 (fallback)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.replace(',', ''))
            if match:
                price_str = match.group().replace('$', '').replace('£', '').replace('€', '').replace(',', '')
                try:
                    return float(price_str)
                except ValueError:
                    continue
        return None
    
    def scrape_amazon_price(self, url):
        """Scrape price from Amazon product page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Multiple price selectors for Amazon
            price_selectors = [
                '.a-price-whole',
                '.a-price .a-offscreen',
                '#priceblock_dealprice',
                '#priceblock_ourprice',
                '.a-price-current',
                '.a-price-symbol + .a-price-whole'
            ]
            
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    price = self.extract_price_from_text(price_text)
                    if price:
                        self.logger.info(f"Amazon price found: ${price}")
                        return price
            
            # Fallback to text search
            text = soup.get_text()
            price = self.extract_price_from_text(text)
            if price:
                self.logger.info(f"Amazon price found (fallback): ${price}")
                return price
                
        except Exception as e:
            self.logger.error(f"Error scraping Amazon: {e}")
        
        return None
    
    def scrape_ebay_price(self, url):
        """Scrape price from eBay product page"""
        try:
            if self.driver is None:
                self.logger.error("Chrome driver not available for eBay scraping")
                return None
                
            self.driver.get(url)
            time.sleep(3)  # Wait for page load
            
            # eBay price selectors
            price_selectors = [
                '[data-testid="x-price-primary"] .text-display-1',
                '.notranslate .text-display-1',
                '#prcIsum_bidPrice',
                '.u-flL.condText',
                '.text-display-1'
            ]
            
            for selector in price_selectors:
                try:
                    price_element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    price_text = price_element.text
                    price = self.extract_price_from_text(price_text)
                    if price:
                        self.logger.info(f"eBay price found: ${price}")
                        return price
                except Exception as e:
                    self.logger.debug(f"Failed to extract price from selector: {e}")
                    continue
            
            # Fallback to page text
            page_text = self.driver.page_source
            soup = BeautifulSoup(page_text, 'html.parser')
            text = soup.get_text()
            price = self.extract_price_from_text(text)
            if price:
                self.logger.info(f"eBay price found (fallback): ${price}")
                return price
                
        except Exception as e:
            self.logger.error(f"Error scraping eBay: {e}")
        
        return None
    
    def get_product_price(self, product):
        """Get current price for a product"""
        url = product['url']
        platform = self.detect_platform(url)
        
        self.logger.info(f"Checking price for: {product['name']} on {platform}")
        
        if platform == 'amazon':
            return self.scrape_amazon_price(url)
        elif platform == 'ebay':
            return self.scrape_ebay_price(url)
        else:
            self.logger.warning(f"Unsupported platform for URL: {url}")
            return None
    
    def detect_platform(self, url):
        """Detect e-commerce platform from URL"""
        if 'amazon.' in url:
            return 'amazon'
        elif 'ebay.' in url:
            return 'ebay'
        else:
            return 'unknown'
    
    def load_price_history(self):
        """Load price history from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading price history: {e}")
        return {}
    
    def save_price_history(self, history):
        """Save price history to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(history, f, indent=4)
        except Exception as e:
            self.logger.error(f"Error saving price history: {e}")
    
    def add_product(self, name, url, target_price=None):
        """Add a new product to monitor"""
        product = {
            "name": name,
            "url": url,
            "target_price": target_price,
            "added_date": datetime.now().isoformat()
        }
        
        self.config["products"].append(product)
        self.save_config()
        
        print(f"{Fore.GREEN}✓ Added product: {name}{Style.RESET_ALL}")
        return True

    def remove_product(self, name):
        """Remove a product by name and clean related history"""
        products = self.config.get("products", [])
        remaining_products = [p for p in products if p.get("name") != name]

        if len(remaining_products) == len(products):
            print(f"{Fore.YELLOW}⚠️ Product not found: {name}{Style.RESET_ALL}")
            return False

        self.config["products"] = remaining_products
        self.save_config()

        history = self.load_price_history()
        if name in history:
            history.pop(name, None)
            self.save_price_history(history)

        self.notify_completion(f"Removed product: {name}")
        return True
    
    def check_all_prices(self):
        """Check prices for all monitored products"""
        history = self.load_price_history()
        
        for product in self.config["products"]:
            try:
                current_price = self.get_product_price(product)
                
                if current_price is not None:
                    product_name = product["name"]
                    
                    # Initialize history for new products
                    if product_name not in history:
                        history[product_name] = []
                    
                    # Add current price to history
                    price_entry = {
                        "price": current_price,
                        "timestamp": datetime.now().isoformat()
                    }
                    history[product_name].append(price_entry)
                    
                    # Check for price drop
                    if len(history[product_name]) > 1:
                        previous_price = history[product_name][-2]["price"]
                        price_change = ((current_price - previous_price) / previous_price) * 100
                        
                        if price_change <= -self.config["price_drop_threshold"]:
                            self.send_price_alert(product, current_price, previous_price, price_change)
                    
                    # Check target price
                    if product.get("target_price") and current_price <= product["target_price"]:
                        self.send_target_price_alert(product, current_price)
                    
                    print(f"{Fore.CYAN}{product_name}: ${current_price:.2f}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}✗ Failed to get price for: {product['name']}{Style.RESET_ALL}")
                    
            except Exception as e:
                self.logger.error(f"Error checking price for {product['name']}: {e}")
        
        self.save_price_history(history)
        self.notify_completion("Finished checking all product prices")
    
    def send_price_alert(self, product, current_price, previous_price, price_change):
        """Send email alert for significant price drop"""
        if not self.config["email"]["enabled"]:
            return
        
        subject = f"Price Drop Alert: {product['name']}"
        body = f"""
        Great news! The price has dropped for {product['name']}
        
        Previous Price: ${previous_price:.2f}
        Current Price: ${current_price:.2f}
        Price Change: {price_change:.1f}%
        
        Product URL: {product['url']}
        
        Happy shopping!
        """
        
        self.send_email(subject, body)
    
    def send_target_price_alert(self, product, current_price):
        """Send email alert when target price is reached"""
        if not self.config["email"]["enabled"]:
            return
        
        subject = f"Target Price Reached: {product['name']}"
        body = f"""
        Your target price has been reached for {product['name']}!
        
        Target Price: ${product['target_price']:.2f}
        Current Price: ${current_price:.2f}
        
        Product URL: {product['url']}
        
        Time to buy!
        """
        
        self.send_email(subject, body)
    
    def send_email(self, subject, body):
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config["email"]["sender_email"]
            msg['To'] = self.config["email"]["recipient_email"]
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.config["email"]["smtp_server"], self.config["email"]["smtp_port"])
            server.starttls()
            server.login(self.config["email"]["sender_email"], self.config["email"]["sender_password"])
            
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email sent: {subject}")
            
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
    
    def start_monitoring(self):
        """Start continuous price monitoring"""
        print(f"{Fore.GREEN}🚀 Starting Price Monitor...{Style.RESET_ALL}")
        print(f"Monitoring {len(self.config['products'])} products")
        print(f"Check interval: {self.config['check_interval']} minutes")
        
        # Schedule price checks
        schedule.every(self.config["check_interval"]).minutes.do(self.check_all_prices)
        
        # Initial check
        self.check_all_prices()
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Monitoring stopped by user{Style.RESET_ALL}")
        finally:
            if self.driver:
                self.driver.quit()
    
    def generate_report(self):
        """Generate price history report"""
        history = self.load_price_history()

        if not history:
            print(f"{Fore.YELLOW}No price history available{Style.RESET_ALL}")
            return

        print(f"\n{Fore.CYAN}📊 Price History Report{Style.RESET_ALL}")
        print("=" * 50)

        for product_name, prices in history.items():
            if prices:
                current_price = prices[-1]["price"]
                min_price = min(p["price"] for p in prices)
                max_price = max(p["price"] for p in prices)
                avg_price = sum(p["price"] for p in prices) / len(prices)

                print(f"\n{Fore.WHITE}{product_name}:{Style.RESET_ALL}")
                print(f"  Current: ${current_price:.2f}")
                print(f"  Minimum: ${min_price:.2f}")
                print(f"  Maximum: ${max_price:.2f}")
                print(f"  Average: ${avg_price:.2f}")
                print(f"  Tracked for: {len(prices)} data points")

        self.notify_completion("Generated price history report")

    def find_ebay_deals(self, search_term, max_price=50, min_bids=0, ending_soon_hours=24):
        """Find eBay auction deals based on search term"""
        print(f"{Fore.CYAN}🔍 Searching for eBay deals: {search_term}{Style.RESET_ALL}")

        # Construct eBay search URL for auctions
        base_url = "https://www.ebay.com/sch/i.html"
        params = {
            '_nkw': search_term,
            'LH_Auction': '1',  # Auctions only
            '_sop': '1',        # Sort by time: newly listed
            '_ipg': '200'       # 200 results per page
        }

        search_url = base_url + '?' + urllib.parse.urlencode(params)

        try:
            if self.driver is None:
                self.logger.error("Chrome driver not available for deal searching")
                return []

            self.driver.get(search_url)
            time.sleep(5)  # Wait for page load

            # Extract auction items
            deals = []
            items = self.driver.find_elements(By.CSS_SELECTOR, '.s-item')

            for item in items[:20]:  # Limit to first 20 for performance
                try:
                    title_element = item.find_element(By.CSS_SELECTOR, '.s-item__title')
                    title = title_element.text.strip()

                    if 'notranslate' in title.lower() or not title:
                        continue

                    # Get price
                    price_element = item.find_element(By.CSS_SELECTOR, '.s-item__price')
                    price_text = price_element.text
                    current_price = self.extract_price_from_text(price_text)

                    if current_price and current_price <= max_price:
                        # Get bid count
                        bid_count = 0
                        try:
                            bid_element = item.find_element(By.CSS_SELECTOR, '.s-item__bidCount')
                            bid_text = bid_element.text
                            bid_match = re.search(r'(\d+)', bid_text)
                            if bid_match:
                                bid_count = int(bid_match.group(1))
                        except Exception as e:
                            self.logger.debug(f"Failed to extract bid count: {e}")

                        if bid_count >= min_bids:
                            # Get end time
                            end_time = None
                            try:
                                time_element = item.find_element(By.CSS_SELECTOR, '.s-item__time-end')
                                time_text = time_element.text
                                if 'ending' in time_text.lower():
                                    # Parse relative time (e.g., "ending today 14:30")
                                    end_time = self.parse_ebay_time(time_text)
                            except Exception as e:
                                self.logger.debug(f"Failed to extract end time: {e}")

                            # Check if ending soon
                            if end_time and datetime.now() + timedelta(hours=ending_soon_hours) > end_time:
                                # Get item URL
                                link_element = item.find_element(By.CSS_SELECTOR, '.s-item__link')
                                item_url = link_element.get_attribute('href')

                                # Generate summary
                                summary = self.generate_deal_summary(title, current_price, bid_count, end_time)

                                deal = {
                                    'title': title,
                                    'price': current_price,
                                    'bid_count': bid_count,
                                    'end_time': end_time.isoformat() if end_time else None,
                                    'url': item_url,
                                    'summary': summary,
                                    'search_term': search_term
                                }

                                deals.append(deal)

                except Exception as e:
                    self.logger.debug(f"Error parsing item: {e}")
                    continue

            # Sort deals by price (lowest first)
            deals.sort(key=lambda x: x['price'])

            print(f"{Fore.GREEN}✅ Found {len(deals)} potential deals{Style.RESET_ALL}")
            return deals

        except Exception as e:
            self.logger.error(f"Error searching eBay deals: {e}")
            return []

    def parse_ebay_time(self, time_text):
        """Parse eBay relative time to datetime"""
        now = datetime.now()
        time_lower = time_text.lower()

        if 'today' in time_lower:
            time_match = re.search(r'(\d{1,2}):(\d{2})', time_text)
            if time_match:
                hour, minute = map(int, time_match.groups())
                return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        elif 'tomorrow' in time_lower:
            time_match = re.search(r'(\d{1,2}):(\d{2})', time_text)
            if time_match:
                hour, minute = map(int, time_match.groups())
                return (now + timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)

        return now + timedelta(hours=1)  # Default fallback

    def generate_deal_summary(self, title, price, bid_count, end_time):
        """Auto-generate a summary for the deal"""
        urgency = "🔥 HOT DEAL" if price < 10 else "💰 Great Deal" if price < 25 else "🛒 Good Deal"

        time_left = ""
        if end_time:
            delta = end_time - datetime.now()
            hours = delta.total_seconds() / 3600
            if hours < 1:
                time_left = "Ending soon!"
            elif hours < 24:
                time_left = f"Ends in {int(hours)}h"
            else:
                time_left = f"Ends in {int(hours/24)}d"

        bid_info = f" ({bid_count} bids)" if bid_count > 0 else " (No bids yet)"

        summary = f"{urgency}: {title[:50]}... at ${price:.2f}{bid_info}. {time_left}"
        return summary

    def display_deals(self, deals):
        """Display found deals in a formatted way"""
        if not deals:
            print(f"{Fore.YELLOW}No deals found matching criteria{Style.RESET_ALL}")
            self.notify_completion("Deal finder completed with no matches")
            return

        print(f"\n{Fore.CYAN}🎯 Top eBay Deals{Style.RESET_ALL}")
        print("=" * 80)

        for i, deal in enumerate(deals[:10], 1):  # Show top 10
            print(f"\n{Fore.GREEN}{i}. {deal['summary']}{Style.RESET_ALL}")
            print(f"   Link: {deal['url']}")

        # Save deals to file
        deals_file = f"ebay_deals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(deals_file, 'w') as f:
                json.dump(deals, f, indent=4)
            print(f"\n{Fore.BLUE}💾 Deals saved to {deals_file}{Style.RESET_ALL}")
        except Exception as e:
            self.logger.error(f"Error saving deals: {e}")
        finally:
            self.notify_completion(f"Deal finder completed - {len(deals)} deal(s) processed")


# CLI Interface
@click.group()
def cli():
    """Professional Price Monitor - Track product prices across major e-commerce sites"""
    pass

@cli.command()
@click.option('--name', prompt='Product name', help='Name of the product to monitor')
@click.option('--url', prompt='Product URL', help='URL of the product page')
@click.option('--target-price', type=float, help='Target price for notifications')
def add(name, url, target_price):
    """Add a new product to monitor"""
    monitor = PriceMonitor()
    monitor.add_product(name, url, target_price)

@cli.command()
def check():
    """Check current prices for all monitored products"""
    monitor = PriceMonitor()
    monitor.check_all_prices()

@cli.command()
def monitor():
    """Start continuous price monitoring"""
    monitor = PriceMonitor()
    monitor.start_monitoring()

@cli.command()
def report():
    """Generate price history report"""
    monitor = PriceMonitor()
    monitor.generate_report()

@cli.command()
@click.option('--search', prompt='Search term', help='What to search for on eBay')
@click.option('--max-price', default=50, type=float, help='Maximum price for deals')
@click.option('--min-bids', default=0, type=int, help='Minimum number of bids')
@click.option('--ending-soon', default=24, type=int, help='Hours until auction ends')
def deals(search, max_price, min_bids, ending_soon):
    """Find eBay auction deals"""
    monitor = PriceMonitor()
    deals = monitor.find_ebay_deals(search, max_price, min_bids, ending_soon)
    monitor.display_deals(deals)

@cli.command()
@click.option('--name', prompt='Product name', help='Name of the product to remove')
def remove(name):
    """Remove a product from monitoring"""
    monitor = PriceMonitor()
    removed = monitor.remove_product(name)
    if not removed:
        click.echo(f"No product named '{name}' was found in the configuration.")

@cli.command()
def setup():
    """Setup email notifications"""
    monitor = PriceMonitor()

    print(f"{Fore.CYAN}📧 Email Setup{Style.RESET_ALL}")

    sender_email = click.prompt("Sender email address")
    sender_password = click.prompt("Sender email password", hide_input=True)
    recipient_email = click.prompt("Recipient email address")

    monitor.config["email"]["enabled"] = True
    monitor.config["email"]["sender_email"] = sender_email
    monitor.config["email"]["sender_password"] = sender_password
    monitor.config["email"]["recipient_email"] = recipient_email

    monitor.save_config()
    print(f"{Fore.GREEN}✓ Email notifications configured{Style.RESET_ALL}")

if __name__ == "__main__":
    cli()
