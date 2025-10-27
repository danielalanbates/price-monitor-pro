#!/bin/bash
# MacOS Price Monitor Installer
# Professional grade installation script

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Paths
INSTALL_DIR="$HOME/.local/bin"
APP_SUPPORT_DIR="$HOME/Library/Application Support/PriceMonitor"
SCRIPT_NAME="price-monitor"

echo -e "${BLUE}🍎 MacOS Price Monitor Installer${NC}"
echo "=================================="

# Check macOS version
macos_version=$(sw_vers -productVersion)
echo "macOS Version: $macos_version"

# Check if we're on macOS 10.14+ (required for notifications)
if [[ $(echo "$macos_version" | cut -d. -f1) -lt 10 ]] || 
   [[ $(echo "$macos_version" | cut -d. -f1) -eq 10 && $(echo "$macos_version" | cut -d. -f2) -lt 14 ]]; then
    echo -e "${RED}❌ macOS 10.14 or later required${NC}"
    exit 1
fi

echo -e "${GREEN}✅ macOS compatibility check passed${NC}"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    echo "Install Python 3 from https://python.org or use Homebrew:"
    echo "  brew install python"
    exit 1
fi

python_version=$(python3 --version | cut -d' ' -f2)
echo "Python Version: $python_version"
echo -e "${GREEN}✅ Python 3 found${NC}"

# Install Python dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
if ! pip3 install requests beautifulsoup4 --user --quiet; then
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Create directories
echo -e "${YELLOW}📁 Creating directories...${NC}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$APP_SUPPORT_DIR"

# Install script
echo -e "${YELLOW}🔧 Installing price monitor...${NC}"
cp macos_price_monitor.py "$INSTALL_DIR/$SCRIPT_NAME"
chmod +x "$INSTALL_DIR/$SCRIPT_NAME"

# Add to PATH if not already there
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo -e "${YELLOW}🛠  Adding to PATH...${NC}"
    
    # Detect shell and add to appropriate config file
    if [[ $SHELL == *"zsh"* ]]; then
        config_file="$HOME/.zshrc"
    elif [[ $SHELL == *"bash"* ]]; then
        config_file="$HOME/.bash_profile"
    else
        config_file="$HOME/.profile"
    fi
    
    echo "" >> "$config_file"
    echo "# Price Monitor" >> "$config_file"
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$config_file"
    
    echo -e "${GREEN}✅ Added to PATH in $config_file${NC}"
    echo -e "${YELLOW}⚠️  Restart your terminal or run: source $config_file${NC}"
fi

# Test installation
echo -e "${YELLOW}🧪 Testing installation...${NC}"
if "$INSTALL_DIR/$SCRIPT_NAME" status &> /dev/null; then
    echo -e "${GREEN}✅ Installation successful!${NC}"
else
    echo -e "${RED}❌ Installation test failed${NC}"
    exit 1
fi

# Create desktop shortcut
echo -e "${YELLOW}🖥  Creating desktop shortcut...${NC}"
cat > "$HOME/Desktop/Price Monitor.command" << EOF
#!/bin/bash
cd "\$HOME"
"$INSTALL_DIR/$SCRIPT_NAME" status
echo ""
echo "Commands:"
echo "  $SCRIPT_NAME add 'URL' 'Product Name'"
echo "  $SCRIPT_NAME check"
echo "  $SCRIPT_NAME status"
echo ""
read -p "Press Enter to continue..."
EOF

chmod +x "$HOME/Desktop/Price Monitor.command"

echo ""
echo -e "${GREEN}🎉 Installation Complete!${NC}"
echo ""
echo "Quick Start:"
echo -e "  ${BLUE}$SCRIPT_NAME add 'https://amazon.com/dp/PRODUCT' 'Product Name'${NC}"
echo -e "  ${BLUE}$SCRIPT_NAME check${NC}"
echo -e "  ${BLUE}$SCRIPT_NAME status${NC}"
echo ""
echo "Features:"
echo "  ✅ Native macOS notifications"
echo "  ✅ Background monitoring (LaunchAgent)"
echo "  ✅ System integration"
echo "  ✅ Secure data storage"
echo ""
echo "Setup background monitoring:"
echo -e "  ${BLUE}$SCRIPT_NAME setup-agent${NC}"
echo ""
echo -e "${GREEN}Happy price monitoring! 🛒💰${NC}"