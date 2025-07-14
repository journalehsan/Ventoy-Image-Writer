#!/usr/bin/env python3
"""
Ventoy Image Writer - A modern PySide6 application for writing ISO images to USB devices
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from image_writer import ImageWriterWindow

def main():
    """Main entry point for the application"""
    print("Starting Ventoy Image Writer...")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Ventoy Image Writer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("VentoyImageWriter")
    
    # High DPI support is enabled by default in Qt 6
    
    try:
        # Create main window
        print("Creating main window...")
        window = ImageWriterWindow()
        window.show()
        
        print("Application started successfully")
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
