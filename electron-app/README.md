# Price Monitor Pro

A professional cross-platform desktop application for monitoring product prices across major e-commerce platforms. Built with Electron for macOS, Windows, and Linux.

## 🚀 Features

- **Real-time Price Monitoring**: Track prices from Amazon, eBay, and other major retailers
- **Smart Notifications**: Get alerted when target prices are reached
- **Price History**: Visual tracking of price changes over time
- **Cross-platform**: Native apps for macOS, Windows, and Linux
- **System Tray Integration**: Run quietly in the background
- **Professional UI**: Modern, responsive interface with dark mode support

## 💻 Platform Support

- **macOS** 10.14+ (Intel & Apple Silicon)
- **Windows** 10/11 (64-bit)
- **Linux** (AppImage format)

## 🛠 Development

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Setup

```bash
# Clone and install dependencies
git clone <repository-url>
cd electron-app
npm install

# Run in development
npm start

# Build for current platform
npm run build

# Build for all platforms
./build.sh
```

### Project Structure

```
electron-app/
├── src/
│   ├── main.js          # Electron main process
│   ├── preload.js       # Secure IPC bridge
│   ├── renderer.js      # Frontend application logic  
│   ├── index.html       # Main UI
│   └── styles.css       # Professional styling
├── package.json         # Dependencies & build config
└── build.sh            # Cross-platform build script
```

## 📦 Building & Distribution

The app uses `electron-builder` for creating distributable packages:

- **macOS**: `.dmg` installer with code signing support
- **Windows**: `.exe` installer with auto-updater
- **Linux**: `.AppImage` portable format

### Gumroad Distribution

Perfect for selling on Gumroad marketplace:
- Professional native app experience
- Cross-platform compatibility 
- Easy installation for customers
- Higher perceived value than web apps

## 🔧 Configuration

The app stores settings and data in platform-appropriate locations:
- **macOS**: `~/Library/Application Support/Price Monitor Pro/`
- **Windows**: `%APPDATA%/Price Monitor Pro/`
- **Linux**: `~/.config/Price Monitor Pro/`

## 📊 Monetization Strategy

Based on market research of successful Gumroad desktop apps:
- **Pricing**: $25-39 for professional utility software
- **Target Audience**: E-commerce sellers, deal hunters, bargain shoppers
- **Value Proposition**: Save money through automated price tracking
- **Competitive Advantage**: Native desktop experience vs web-based tools

## 🔒 Security & Privacy

- No data collection or tracking
- All price monitoring happens locally
- Secure web scraping with proper rate limiting
- Encrypted local data storage

## 📈 Features Roadmap

- [ ] Browser extension integration
- [ ] Bulk product import/export
- [ ] Advanced filtering and search
- [ ] Price prediction algorithms  
- [ ] Team/sharing features
- [ ] Mobile companion app

## 🤝 Contributing

This is a commercial project. For feature requests or bug reports, please contact support.

## 📄 License

Commercial license. Not for redistribution.

---

**Ready to launch on Gumroad and start earning that $10+ monthly!** 🎯