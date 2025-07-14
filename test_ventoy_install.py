#!/usr/bin/env python3
"""
Test script to verify Ventoy installation with automatic confirmation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from helper.ventoy_manager import VentoyManager

class MockProgressWidget:
    """Mock progress widget for testing"""
    
    def __init__(self):
        self.logs = []
        self.progress = 0
        self.status = ""
    
    def add_log(self, message):
        print(f"LOG: {message}")
        self.logs.append(message)
    
    def set_progress(self, value):
        print(f"PROGRESS: {value}%")
        self.progress = value
    
    def set_status(self, message):
        print(f"STATUS: {message}")
        self.status = message
    
    def finish_operation(self, success, message):
        result = "SUCCESS" if success else "FAILED"
        print(f"FINISHED: {result} - {message}")

def test_ventoy_installation():
    """Test Ventoy installation with automatic confirmation"""
    print("Testing Ventoy Installation with Auto-confirmation")
    print("=" * 60)
    
    # Check if we have USB devices
    import subprocess
    try:
        result = subprocess.run(['lsblk', '-d', '-o', 'NAME,SIZE,TYPE,TRAN'], 
                               capture_output=True, text=True, check=True)
        print("Available USB devices:")
        for line in result.stdout.split('\n'):
            if 'usb' in line:
                print(f"  {line}")
        
        # Use /dev/sdc for testing (if available)
        device = "/dev/sdc"
        
        print(f"\nTesting installation on {device}")
        print("WARNING: This will format the device!")
        
        response = input(f"Continue with test installation on {device}? (y/n): ")
        if response.lower() != 'y':
            print("Test cancelled by user")
            return
        
        # Create mock progress widget
        progress_widget = MockProgressWidget()
        
        # Create Ventoy manager and test installation
        ventoy_manager = VentoyManager()
        
        print("\nStarting Ventoy installation test...")
        ventoy_manager.install_ventoy(device, progress_widget)
        
        print("\nTest completed!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ventoy_installation()
