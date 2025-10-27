#!/bin/bash

# Price Monitor Pro - Complete Application Launcher
# This script sets up and launches both the Python backend and Electron frontend

echo "🚀 Starting Price Monitor Pro..."

# Check if we're in the right directory
if [ ! -f "price_monitor.py" ]; then
    echo "❌ Error: price_monitor.py not found. Please run this script from the Price_Monitor_Scraper directory."
    exit 1
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not found."
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install requests beautifulsoup4 lxml selenium webdriver-manager click colorama schedule

# Check Node.js installation
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is required but not found."
    exit 1
fi

# Check npm installation
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is required but not found."
    exit 1
fi

# Install Electron dependencies
echo "📦 Installing Electron dependencies..."
cd electron-app
npm install

# Go back to main directory
cd ..

echo "✅ Setup complete!"
echo ""
echo "🎯 Choose how to run the application:"
echo ""
echo "1. CLI Only (Python deal finder):"
echo "   python3 price_monitor.py deals --search \"iPhone\" --max-price 100 --ending-soon 12"
echo ""
echo "2. Full Desktop App (Electron + Python backend):"
echo "   cd electron-app && npm start"
echo ""
echo "3. Development mode:"
echo "   cd electron-app && npm run dev"
echo ""
echo "🔥 Features available:"
echo "   - Price monitoring for Amazon & eBay"
echo "   - Real-time eBay auction deal finding"
echo "   - Automated price alerts and notifications"
echo "   - Professional desktop interface"
echo ""
echo "Happy deal hunting! 🛒"
