#!/usr/bin/env python3
"""
Image Writer Main Window - Modern PySide6 window with fluent design
"""

import os
import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QProgressBar, QTextEdit, 
                               QGroupBox, QFileDialog, QMessageBox, QComboBox)
from PySide6.QtCore import Qt, QThread, QTimer, Signal, QSize
from PySide6.QtGui import QFont, QPalette, QColor, QIcon

from widgets.modern_button import ModernButton
from widgets.device_selector import DeviceSelector
from widgets.progress_widget import ProgressWidget
from helper.ventoy_manager import VentoyManager
from helper.usb_detector import USBDetector
from helper.file_operations import FileOperations

class ImageWriterWindow(QMainWindow):
    """Main window for the Image Writer application"""
    
    def __init__(self):
        super().__init__()
        print("Initializing ImageWriterWindow...")
        
        try:
            print("Creating VentoyManager...")
            self.ventoy_manager = VentoyManager()
            
            print("Creating USBDetector...")
            self.usb_detector = USBDetector()
            
            print("Creating FileOperations...")
            self.file_ops = FileOperations()
            
            self.selected_images = []
            self.selected_device = None
            self.active_threads = []
            
            print("Setting up UI...")
            self.setup_ui()
            
            print("Setting up connections...")
            self.setup_connections()
            
            print("Refreshing devices...")
            self.refresh_devices()
            
            print("ImageWriterWindow initialized successfully")
        except Exception as e:
            print(f"Error initializing ImageWriterWindow: {e}")
            import traceback
            traceback.print_exc()
            raise
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Ventoy Image Writer")
        self.setMinimumSize(600, 500)
        self.resize(800, 600)
        
        # Apply modern styling
        self.setStyleSheet(self.get_modern_style())
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Ventoy Image Writer")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Image selection group
        image_group = QGroupBox("Image Selection")
        image_layout = QVBoxLayout(image_group)
        
        # Selected images display
        self.images_text = QTextEdit()
        self.images_text.setMaximumHeight(100)
        self.images_text.setPlaceholderText("No images selected...")
        self.images_text.setReadOnly(True)
        image_layout.addWidget(self.images_text)
        
        # Image selection buttons
        image_buttons_layout = QHBoxLayout()
        self.select_images_btn = ModernButton("Select Images")
        self.clear_images_btn = ModernButton("Clear")
        self.clear_images_btn.setEnabled(False)
        
        image_buttons_layout.addWidget(self.select_images_btn)
        image_buttons_layout.addWidget(self.clear_images_btn)
        image_buttons_layout.addStretch()
        
        image_layout.addLayout(image_buttons_layout)
        main_layout.addWidget(image_group)
        
        # Device selection
        device_group = QGroupBox("USB Device Selection")
        device_layout = QVBoxLayout(device_group)
        
        self.device_selector = DeviceSelector()
        device_layout.addWidget(self.device_selector)
        
        device_buttons_layout = QHBoxLayout()
        self.refresh_devices_btn = ModernButton("Refresh Devices")
        device_buttons_layout.addWidget(self.refresh_devices_btn)
        device_buttons_layout.addStretch()
        
        device_layout.addLayout(device_buttons_layout)
        main_layout.addWidget(device_group)
        
        # Ventoy options
        ventoy_group = QGroupBox("Ventoy Options")
        ventoy_layout = QVBoxLayout(ventoy_group)
        
        self.install_ventoy_btn = ModernButton("Install Ventoy")
        self.install_ventoy_btn.setEnabled(False)
        
        ventoy_layout.addWidget(self.install_ventoy_btn)
        main_layout.addWidget(ventoy_group)
        
        # Progress section
        self.progress_widget = ProgressWidget()
        main_layout.addWidget(self.progress_widget)
        
        # Action buttons
        action_layout = QHBoxLayout()
        self.write_images_btn = ModernButton("Write Images")
        self.write_images_btn.setEnabled(False)
        self.write_images_btn.setObjectName("primaryButton")
        
        action_layout.addStretch()
        action_layout.addWidget(self.write_images_btn)
        
        main_layout.addLayout(action_layout)
        
    def setup_connections(self):
        """Setup signal connections"""
        self.select_images_btn.clicked.connect(self.select_images)
        self.clear_images_btn.clicked.connect(self.clear_images)
        self.refresh_devices_btn.clicked.connect(self.refresh_devices)
        self.install_ventoy_btn.clicked.connect(self.install_ventoy)
        self.write_images_btn.clicked.connect(self.write_images)
        self.device_selector.device_selected.connect(self.on_device_selected)
        
    def select_images(self):
        """Open file dialog to select ISO images"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("ISO Images (*.iso);;All Files (*)")
        file_dialog.setWindowTitle("Select ISO Images")
        
        if file_dialog.exec():
            self.selected_images = file_dialog.selectedFiles()
            self.update_images_display()
            self.clear_images_btn.setEnabled(True)
            self.update_write_button_state()
            
    def clear_images(self):
        """Clear selected images"""
        self.selected_images = []
        self.update_images_display()
        self.clear_images_btn.setEnabled(False)
        self.update_write_button_state()
        
    def update_images_display(self):
        """Update the images display text"""
        if not self.selected_images:
            self.images_text.setText("No images selected...")
        else:
            text = "Selected Images:\\n"
            for img in self.selected_images:
                text += f"• {os.path.basename(img)}\\n"
            self.images_text.setText(text)
            
    def refresh_devices(self):
        """Refresh the list of USB devices"""
        devices = self.usb_detector.get_usb_devices()
        self.device_selector.update_devices(devices)
        
    def on_device_selected(self, device):
        """Handle device selection"""
        self.selected_device = device
        self.install_ventoy_btn.setEnabled(device is not None)
        self.update_write_button_state()
        
        # Check if device already has Ventoy
        if device and self.ventoy_manager.has_ventoy(device):
            self.progress_widget.set_status("Ventoy partition detected on device")
        else:
            self.progress_widget.set_status("Device selected - Ventoy not detected")
            
    def update_write_button_state(self):
        """Update the write button enabled state"""
        has_images = len(self.selected_images) > 0
        has_device = self.selected_device is not None
        self.write_images_btn.setEnabled(has_images and has_device)
        
    def install_ventoy(self):
        """Install Ventoy on the selected device"""
        if not self.selected_device:
            QMessageBox.warning(self, "No Device", "Please select a USB device first.")
            return
            
        reply = QMessageBox.question(
            self, 
            "Install Ventoy", 
            f"This will format the device {self.selected_device}. All data will be lost. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.progress_widget.start_operation("Installing Ventoy...")
            self.ventoy_manager.install_ventoy(self.selected_device, self.progress_widget)
            
    def write_images(self):
        """Write selected images to the device"""
        if not self.selected_images or not self.selected_device:
            QMessageBox.warning(self, "Missing Selection", "Please select both images and a device.")
            return
            
        # Check if Ventoy is installed
        if not self.ventoy_manager.has_ventoy(self.selected_device):
            reply = QMessageBox.question(
                self,
                "Ventoy Not Found",
                "Ventoy is not installed on this device. Install it first?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.install_ventoy()
                return
            else:
                return
                
        # Start writing images
        self.progress_widget.start_operation("Writing images...")
        self.file_ops.copy_images_to_ventoy(
            self.selected_images, 
            self.selected_device, 
            self.progress_widget
        )
        
    def get_modern_style(self):
        """Get modern fluent design stylesheet"""
        return """
        QMainWindow {
            background-color: #f3f3f3;
            color: #202020;
        }
        
        QLabel#title {
            font-size: 24px;
            font-weight: bold;
            color: #0078d4;
            padding: 10px;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #e1e1e1;
            border-radius: 8px;
            margin-top: 1ex;
            padding-top: 10px;
            background-color: white;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #0078d4;
        }
        
        QTextEdit {
            border: 1px solid #e1e1e1;
            border-radius: 4px;
            padding: 8px;
            background-color: white;
            selection-background-color: #0078d4;
        }
        
        QComboBox {
            border: 1px solid #e1e1e1;
            border-radius: 4px;
            padding: 8px;
            background-color: white;
            min-height: 20px;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #666;
            margin-right: 5px;
        }
        
        QProgressBar {
            border: 1px solid #e1e1e1;
            border-radius: 4px;
            text-align: center;
            background-color: #f0f0f0;
        }
        
        QProgressBar::chunk {
            background-color: #0078d4;
            border-radius: 3px;
        }
        """
    
    def closeEvent(self, event):
        """Handle window close event"""
        print("Closing application...")
        self.cleanup()
        event.accept()
        
    def cleanup(self):
        """Clean up resources before closing"""
        try:
            print("Cleaning up resources...")
            
            # Stop any active threads
            for thread in self.active_threads:
                if thread.isRunning():
                    print(f"Stopping thread: {thread}")
                    thread.quit()
                    thread.wait(1000)  # Wait up to 1 second
                    if thread.isRunning():
                        thread.terminate()
                        thread.wait(1000)
            
            # Clean up managers
            if hasattr(self, 'ventoy_manager'):
                self.ventoy_manager.cleanup()
                
            if hasattr(self, 'file_ops'):
                self.file_ops.cleanup()
                
            print("Cleanup completed")
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
