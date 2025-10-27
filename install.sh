#!/bin/bash
# Installation script for Price Monitor Scraper

echo "🛒 Installing Price Monitor Scraper..."

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 from https://python.org"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements_minimal.txt

# Make scripts executable
chmod +x simple_monitor.py
chmod +x price_monitor_pro.py

echo "✅ Installation complete!"
echo ""
echo "🚀 Quick Start:"
echo "python3 simple_monitor.py --url 'PRODUCT_URL' --name 'PRODUCT_NAME'"
echo ""
echo "💎 For unlimited features, get the PRO version:"
echo "https://gumroad.com/l/price-monitor-pro"