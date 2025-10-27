#!/bin/bash

# Price Monitor Pro - Build Script
# Builds the Electron app for all platforms

echo "🚀 Building Price Monitor Pro for all platforms..."

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/

# Build for all platforms
echo "🔨 Building for macOS..."
npm run build:mac

echo "🔨 Building for Windows..."
npm run build:win

echo "🔨 Building for Linux..."
npm run build:linux

echo "✅ Build complete! Check the dist/ folder for your platform-specific packages."
echo ""
echo "📋 Build Results:"
echo "   • macOS: dist/Price Monitor Pro-*.dmg"
echo "   • Windows: dist/Price Monitor Pro Setup *.exe"
echo "   • Linux: dist/Price Monitor Pro-*.AppImage"
echo ""
echo "🎯 Ready for Gumroad distribution!"