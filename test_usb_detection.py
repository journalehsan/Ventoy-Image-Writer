#!/usr/bin/env python3
"""
Test script to verify USB detection functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from helper.usb_detector import USBDetector
from helper.ventoy_manager import VentoyManager

def test_usb_detection():
    """Test USB device detection"""
    print("Testing USB device detection...")
    
    detector = USBDetector()
    devices = detector.get_usb_devices()
    
    print(f"Found {len(devices)} USB device(s):")
    for device in devices:
        print(f"  - {device['path']}: {device['size']} GB ({device['model']})")
    
    return devices

def test_ventoy_detection(devices):
    """Test Ventoy detection on devices"""
    print("\nTesting Ventoy detection...")
    
    ventoy_manager = VentoyManager()
    
    for device in devices:
        has_ventoy = ventoy_manager.has_ventoy(device['path'])
        print(f"  - {device['path']}: {'Has Ventoy' if has_ventoy else 'No Ventoy'}")
        
        if has_ventoy:
            info = ventoy_manager.get_ventoy_info(device['path'])
            print(f"    Partitions: {len(info['partitions'])}")
            for partition in info['partitions']:
                print(f"      - {partition['name']}: {partition['size']} ({partition['label']})")

def main():
    """Main test function"""
    print("Ventoy Image Writer - USB Detection Test")
    print("=" * 50)
    
    try:
        devices = test_usb_detection()
        test_ventoy_detection(devices)
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
