#!/usr/bin/env python3
"""
Modern Button Widget - Fluent Design styled button
"""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QPainter, QColor, QBrush, QPen

class ModernButton(QPushButton):
    """Modern styled button with fluent design animations"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setMinimumWidth(120)
        self.setCursor(Qt.PointingHandCursor)
        self.apply_style()
        
    def apply_style(self):
        """Apply modern button styling"""
        self.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #e1e1e1;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                color: #202020;
                min-height: 24px;
            }
            
            QPushButton:hover {
                background-color: #f8f8f8;
                border-color: #0078d4;
            }
            
            QPushButton:pressed {
                background-color: #f0f0f0;
                border-color: #005a9e;
            }
            
            QPushButton:disabled {
                background-color: #f5f5f5;
                border-color: #e8e8e8;
                color: #a6a6a6;
            }
            
            QPushButton#primaryButton {
                background-color: #0078d4;
                color: white;
                border-color: #0078d4;
            }
            
            QPushButton#primaryButton:hover {
                background-color: #106ebe;
                border-color: #106ebe;
            }
            
            QPushButton#primaryButton:pressed {
                background-color: #005a9e;
                border-color: #005a9e;
            }
            
            QPushButton#primaryButton:disabled {
                background-color: #cccccc;
                border-color: #cccccc;
                color: #666666;
            }
        """)
        
    def enterEvent(self, event):
        """Handle mouse enter event"""
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave event"""
        super().leaveEvent(event)
