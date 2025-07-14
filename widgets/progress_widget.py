#!/usr/bin/env python3
"""
Progress Widget - Shows operation progress and status
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QTextEdit
from PySide6.QtCore import Qt, Signal, QTimer

class ProgressWidget(QWidget):
    """Widget for displaying operation progress"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-weight: bold; color: #0078d4;")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)
        
        # Log area
        self.log_area = QTextEdit()
        self.log_area.setMaximumHeight(100)
        self.log_area.setReadOnly(True)
        self.log_area.setVisible(False)
        self.log_area.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #e1e1e1;
                border-radius: 4px;
                font-family: monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.log_area)
        
    def set_status(self, message):
        """Set the status message"""
        self.status_label.setText(message)
        
    def start_operation(self, operation_name):
        """Start an operation"""
        self.status_label.setText(f"Running: {operation_name}")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.log_area.setVisible(True)
        self.log_area.clear()
        self.add_log(f"Started: {operation_name}")
        
    def set_progress(self, value):
        """Set progress value (0-100)"""
        self.progress_bar.setValue(value)
        
    def add_log(self, message):
        """Add a log message"""
        self.log_area.append(message)
        # Auto-scroll to bottom
        cursor = self.log_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_area.setTextCursor(cursor)
        
    def finish_operation(self, success=True, message=""):
        """Finish the current operation"""
        if success:
            self.status_label.setText("Operation completed successfully")
            self.status_label.setStyleSheet("font-weight: bold; color: #107c10;")
            self.progress_bar.setValue(100)
            if message:
                self.add_log(f"Success: {message}")
        else:
            self.status_label.setText("Operation failed")
            self.status_label.setStyleSheet("font-weight: bold; color: #d13438;")
            if message:
                self.add_log(f"Error: {message}")
                
        # Hide progress bar after a delay
        QTimer.singleShot(3000, self.hide_progress)
        
    def hide_progress(self):
        """Hide the progress bar"""
        self.progress_bar.setVisible(False)
        self.status_label.setStyleSheet("font-weight: bold; color: #0078d4;")
        
    def reset(self):
        """Reset the progress widget"""
        self.status_label.setText("Ready")
        self.status_label.setStyleSheet("font-weight: bold; color: #0078d4;")
        self.progress_bar.setVisible(False)
        self.log_area.setVisible(False)
        self.log_area.clear()
