#!/bin/bash
# Ventoy Image Writer Installation Script

set -e

echo "Installing Ventoy Image Writer..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Error: Please do not run this script as root"
    exit 1
fi

# Create directories
mkdir -p ~/.local/share/bin
mkdir -p ~/.local/share/applications

# Check if we need to build
if [ ! -f "dist/main" ]; then
    echo "Building application..."
    
    # Check for Python and pip
    if ! command -v python3 &> /dev/null; then
        echo "Error: Python 3 is required but not installed"
        exit 1
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    # Build with PyInstaller
    echo "Building standalone executable..."
    pyinstaller --onefile --windowed main.py
    
    echo "Build completed successfully!"
fi

# Install the binary
echo "Installing binary to ~/.local/share/bin/ventoy-image-writer..."
cp dist/main ~/.local/share/bin/ventoy-image-writer
chmod +x ~/.local/share/bin/ventoy-image-writer

# Install desktop entry
echo "Installing desktop entry..."
cp ventoy-image-writer.desktop ~/.local/share/applications/
chmod +x ~/.local/share/applications/ventoy-image-writer.desktop

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database ~/.local/share/applications/
fi

echo ""
echo "Installation completed successfully!"
echo ""
echo "You can now:"
echo "  1. Run from terminal: ~/.local/share/bin/ventoy-image-writer"
echo "  2. Launch from application menu: Search for 'Ventoy Image Writer'"
echo ""
echo "Make sure ~/.local/share/bin is in your PATH to run from anywhere:"
echo "  export PATH=\$PATH:~/.local/share/bin"
echo ""
