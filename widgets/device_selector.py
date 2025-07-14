#!/usr/bin/env python3
"""
Device Selector Widget - ComboBox for selecting USB devices
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Qt, Signal

class DeviceSelector(QWidget):
    """Widget for selecting USB devices"""
    
    device_selected = Signal(str)  # Emitted when device is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.devices = []
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Device selection combo box
        self.device_combo = QComboBox()
        self.device_combo.setPlaceholderText("Select a USB device...")
        self.device_combo.currentTextChanged.connect(self.on_device_changed)
        
        # Device info layout
        info_layout = QHBoxLayout()
        
        # Device info labels
        self.device_info_label = QLabel("No device selected")
        self.device_info_label.setStyleSheet("color: #666666; font-size: 12px;")
        
        info_layout.addWidget(self.device_info_label)
        info_layout.addStretch()
        
        layout.addWidget(self.device_combo)
        layout.addLayout(info_layout)
        
    def update_devices(self, devices):
        """Update the list of available devices"""
        self.devices = devices
        self.device_combo.clear()
        
        if not devices:
            self.device_combo.addItem("No USB devices found")
            self.device_combo.setEnabled(False)
            self.device_info_label.setText("No USB devices detected")
        else:
            self.device_combo.setEnabled(True)
            self.device_combo.addItem("Select a USB device...")
            
            for device in devices:
                display_text = f"{device['path']} - {device['size']} ({device['model']})"
                self.device_combo.addItem(display_text, device['path'])
                
            self.device_info_label.setText(f"Found {len(devices)} USB device(s)")
            
    def on_device_changed(self, text):
        """Handle device selection change"""
        if text == "Select a USB device..." or text == "No USB devices found":
            self.device_selected.emit("")
            self.device_info_label.setText("No device selected")
            return
            
        # Get the selected device path
        current_index = self.device_combo.currentIndex()
        if current_index > 0:  # Skip the placeholder item
            device_path = self.device_combo.itemData(current_index)
            if device_path:
                self.device_selected.emit(device_path)
                
                # Find device info
                for device in self.devices:
                    if device['path'] == device_path:
                        info_text = f"Selected: {device['path']} - {device['size']} GB"
                        self.device_info_label.setText(info_text)
                        break
                        
    def get_selected_device(self):
        """Get the currently selected device path"""
        current_index = self.device_combo.currentIndex()
        if current_index > 0:
            return self.device_combo.itemData(current_index)
        return None
