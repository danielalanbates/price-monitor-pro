# Price Monitor Pro

🛍️ **Professional price tracking tool for Amazon, eBay & more**

Never miss a deal again! Automatically track product prices across multiple platforms and get notified when they drop.

## Features

### FREE Version (This Repository)
- Monitor 1 product
- Amazon & eBay support
- Price history (last 10 checks)
- Command-line interface
- Local data storage
- eBay Deal Finder - Find low-price auctions
- Auto-generated summaries and links

### PRO Version - $25 One-Time Purchase
- ✨ **UNLIMITED products**
- 📧 Email notifications when prices drop
- ⏰ Automated scheduling (check every X minutes)
- 📊 Advanced analytics & price charts
- 🎯 Target price alerts with smart notifications
- 🔄 Continuous monitoring in background
- 📁 CSV export of price history
- 🖥️ **Beautiful Electron desktop app** with custom icons
- 🔵 eBay deal finder with real-time auction monitoring
- 🍎 **macOS native integration** (notifications, LaunchAgent)
- 🌐 **Multi-platform comparison** (see prices from all sources at once)

## Quick Start

### One-Click Setup (Recommended)
```bash
git clone https://github.com/yourusername/price-monitor-scraper
cd price-monitor-scraper
./launch.sh
```

### Manual Installation
```bash
# Install Python dependencies
pip install requests beautifulsoup4 lxml selenium webdriver-manager click colorama schedule

# Install Electron app dependencies
cd electron-app
npm install
cd ..
```

### Usage

#### CLI Deal Finder
```bash
# Find eBay auction deals
python3 price_monitor.py deals --search "iPhone" --max-price 100 --ending-soon 12

# Find deals with specific filters
python3 price_monitor.py deals --search "vintage guitar" --max-price 200 --min-bids 1 --ending-soon 6
```

#### Desktop Application
```bash
# Launch full desktop app
cd electron-app && npm start

# Development mode
cd electron-app && npm run dev
```

### Example Output for Deals
```
Searching for eBay deals: iPhone

Top eBay Deals
================================================================================

1. HOT DEAL: Apple iPhone 12 64GB Black - Excellent Condition... at $45.00 (3 bids). Ends in 5h
   Link: https://ebay.com/itm/...

2. Great Deal: iPhone 11 Pro Max 256GB Space Gray... at $75.50 (1 bids). Ends in 8h
   Link: https://ebay.com/itm/...

Deals saved to ebay_deals_20251023_140000.json
```

## Installation & Setup

### Requirements
- Python 3.7+
- Internet connection
- Works on: Windows, macOS, Linux

### Dependencies
```bash
pip install requests beautifulsoup4 lxml selenium webdriver-manager click colorama
```

## How It Works

1. Scrapes product pages using intelligent price detection
2. Stores price history in local JSON file
3. Analyzes trends and shows price changes
4. FREE version limited to 1 product (upgrade for unlimited!)

## Ethical & Legal

- Respects robots.txt
- Reasonable request delays
- No aggressive scraping
- Personal use only

*This tool is for personal price monitoring only. Please respect website terms of service.*

## Supported Websites

| Website | Status | Notes |
|---------|--------|-------|
| Amazon | ✅ Full Support | All regions (.com, .co.uk, .ca, etc.) |
| eBay | ✅ Full Support | Auctions & Buy It Now |
| Google Shopping | ⚠️ Experimental | PRO version only |

## Recent Updates (v2.0.0 - October 2025)

- ✅ **Rebranded to Price Monitor Pro** with new professional branding
- ✅ **Multi-platform result display** - See Amazon and eBay prices side-by-side
- ✅ **Enhanced product cards** - Platform-specific titles and prices
- ✅ **Fixed Details button** - Fully functional product detail modal
- ✅ **eBay deals default search** - Defaults to "*" (all items) when empty
- ✅ **Professional app icons** - Custom-designed PNG and ICNS icons
- ✅ **Consolidated dependencies** - Single requirements.txt with clear documentation
- ✅ **Improved error handling** - Better logging and user-friendly error messages
- ✅ **Updated Python packages** - Latest versions of all dependencies

## Why Upgrade to PRO?

| Feature | FREE | PRO |
|---------|------|-----|
| Products to monitor | 1 | Unlimited |
| Price history | 10 entries | Full history |
| Email alerts | No | Yes |
| Automated monitoring | No | Yes |
| Target price alerts | No | Yes |
| CSV export | No | Yes |
| GUI interface | No | Yes |

[Buy PRO Version - $25](https://gumroad.com/l/price-monitor-pro)

## Support

- Email: your-email@domain.com
- Issues: [GitHub Issues](https://github.com/yourusername/price-monitor-scraper/issues)

## License

FREE Version: MIT License
PRO Version: Commercial License
