# 🍎 MacOS Price Monitor

**Professional-grade price tracking with native macOS integration**

![macOS](https://img.shields.io/badge/macOS-10.14+-blue.svg)
![Python](https://img.shields.io/badge/Python-3.7+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Never miss a deal again! Get native macOS notifications when prices drop on your favorite products.

## ✨ Features

### 🎯 **Core Functionality**
- ✅ **Amazon & eBay** price monitoring
- ✅ **Target price alerts** - get notified when YOUR price is reached
- ✅ **Price history tracking** with trend analysis
- ✅ **Smart price detection** with multiple fallback methods
- ✅ **3 products free** (generous free tier)

### 🍎 **macOS Integration**
- 🔔 **Native notifications** with system sounds
- 📊 **Console.app logging** for debugging
- 🚀 **LaunchAgent support** for background monitoring
- 💾 **Proper data storage** in `~/Library/Application Support`
- 🎨 **Terminal-friendly** with colored output
- 🛡️ **System integration** following Apple guidelines

### 🔧 **Advanced Features**
- 📈 **Automatic retry** with exponential backoff
- 🌐 **Smart User-Agent** detection based on your macOS version
- 📝 **Comprehensive logging** to system log
- ⚡ **Fast and reliable** scraping
- 🔒 **Privacy-focused** - all data stored locally

---

## 🚀 Quick Installation

### One-Line Install:
```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/price-monitor/main/install_macos.sh | bash
```

### Manual Install:
```bash
# Clone repository
git clone https://github.com/yourusername/price-monitor-scraper
cd price-monitor-scraper

# Run installer
./install_macos.sh
```

**Requirements:** macOS 10.14+, Python 3.7+

---

## 📖 Usage Examples

### Add Products to Monitor
```bash
# Add Amazon product with target price
price-monitor add "https://amazon.com/dp/B08N5WRWNW" "iPhone 13 Pro" --target 899.99

# Add eBay auction
price-monitor add "https://ebay.com/itm/123456789" "MacBook Pro M1"

# Add any website (experimental)
price-monitor add "https://store.com/product" "Cool Gadget"
```

### Check Current Prices
```bash
# Check all products
price-monitor check

# Quiet check (good for automation)
price-monitor check --quiet
```

### View Status & Analytics
```bash
# Comprehensive status
price-monitor status
```

**Sample Output:**
```
📊 PRICE MONITORING STATUS
==================================================

🏷️  iPhone 13 Pro (Amazon)
   Current:     $899.99
   Lowest:      $849.99
   Highest:     $999.99
   Average:     $924.99
   Tracked:     15 times
   Max Savings: $150.00
   🎯 Target: $899.99 (TARGET REACHED!)
   📉 Recent: -5.2%

💰 Total potential savings tracked: $150.00
📊 Monitoring 1/3 products (free tier)
```

### Background Monitoring
```bash
# Setup automated checking
price-monitor setup-agent

# Load the background service
launchctl load ~/Library/LaunchAgents/com.priceMonitor.agent.plist

# Stop background service
launchctl unload ~/Library/LaunchAgents/com.priceMonitor.agent.plist
```

---

## 🔔 Notifications

Get beautiful native macOS notifications when:
- 📉 **Prices drop** by your threshold (default: 5%)
- 🎯 **Target prices** are reached
- ✅ **Products added** successfully

**Notification Features:**
- System sounds (customizable)
- Action buttons (coming soon)
- Persistent alerts for important deals
- Integration with Notification Center

---

## 🛠️ Configuration

### Data Storage
- **Config:** `~/Library/Application Support/PriceMonitor/config.json`
- **Data:** `~/Library/Application Support/PriceMonitor/price_data.json`
- **Logs:** Viewable in Console.app (search "PriceMonitor")

### Customization
```json
{
  "notifications": {
    "enabled": true,
    "sound": "Glass",
    "persistent": false
  },
  "monitoring": {
    "check_interval": 3600,
    "price_drop_threshold": 5.0
  },
  "max_products_free": 3
}
```

---

## 🌐 Supported Websites

| Website | Status | Notes |
|---------|--------|-------|
| **Amazon** | ✅ Full Support | All regions (.com, .co.uk, .ca, etc.) |
| **eBay** | ✅ Full Support | Auctions & Buy It Now |
| **Generic** | ⚠️ Experimental | Basic price detection |

---

## 🔧 Advanced Usage

### LaunchAgent (Background Monitoring)
```bash
# Create and load background service
price-monitor setup-agent
launchctl load ~/Library/LaunchAgents/com.priceMonitor.agent.plist

# Check logs
tail -f ~/Library/Application\ Support/PriceMonitor/monitor.log
```

### System Integration
- **Logs:** `Console.app` → Search "PriceMonitor"
- **Notifications:** System Preferences → Notifications
- **Data:** `~/Library/Application Support/PriceMonitor/`

### Troubleshooting
```bash
# Check system logs
log show --predicate 'senderImagePath contains "PriceMonitor"' --last 1h

# Test notifications
osascript -e 'display notification "Test message" with title "Price Monitor"'

# Reset data
rm -rf ~/Library/Application\ Support/PriceMonitor/
```

---

## 🎯 Why This Script is Great

### 🍎 **Native macOS Experience**
- Follows Apple Human Interface Guidelines
- Proper system integration and data storage
- Native notifications that respect user preferences
- Console.app integration for debugging

### 🔒 **Privacy & Security**
- All data stored locally
- No external servers or tracking
- Respects website terms of service
- Ethical scraping practices

### ⚡ **Performance**
- Efficient scraping with retry logic
- Minimal system resource usage
- Smart caching and data management
- Optimized for macOS

### 🛠️ **Professional Quality**
- Comprehensive error handling
- Proper logging and debugging
- Clean, maintainable code
- Extensive documentation

---

## 🔄 Cross-Platform Foundation

This macOS version is designed as the foundation for:
- 🐧 **Linux version** (Ubuntu focus)
- 🪟 **Windows 11 version**
- 📱 **iOS shortcuts integration**
- 🤖 **Android Tasker integration**

**Current Focus:** Perfecting the macOS experience first, then expanding to other platforms.

---

## 🤝 Contributing

```bash
# Development setup
git clone https://github.com/yourusername/price-monitor-scraper
cd price-monitor-scraper
pip3 install -r requirements_minimal.txt

# Test on macOS
python3 macos_price_monitor.py --help
```

### Roadmap
- [ ] Menu bar app (SwiftUI)
- [ ] Chrome/Safari extension
- [ ] iOS Shortcuts integration
- [ ] More websites support
- [ ] Price prediction algorithms

---

## 📄 License

**MIT License** - Feel free to modify and distribute

### Commercial Use
- ✅ Personal use
- ✅ Commercial use
- ✅ Modification allowed
- ❌ Warranty not provided

---

## 🆘 Support

### Community
- **Issues:** [GitHub Issues](https://github.com/yourusername/price-monitor-scraper/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/price-monitor-scraper/discussions)

### Compatibility
- **Tested on:** macOS Monterey (12.0+), macOS Ventura (13.0+), macOS Sonoma (14.0+)
- **Python:** 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- **Architectures:** Intel x64, Apple Silicon (M1/M2/M3)

---

**Built with ❤️ for macOS users who love great deals!**

*Happy price monitoring! 🛒💰*