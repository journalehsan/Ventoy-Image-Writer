#!/usr/bin/env python3
"""
USB Detector - Detects and manages USB devices
"""

import subprocess
import re
import os
import json
from typing import List, Dict, Optional

class USBDetector:
    """Class for detecting USB devices"""
    
    def __init__(self):
        self.devices = []
        
    def get_usb_devices(self) -> List[Dict]:
        """Get list of USB storage devices"""
        devices = []
        
        try:
            # Use lsblk to get block devices
            result = subprocess.run([
                'lsblk', '-J', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT,MODEL,VENDOR,TRAN'
            ], capture_output=True, text=True, check=True)
            
            data = json.loads(result.stdout)
            
            for device in data.get('blockdevices', []):
                # Only include USB devices that are disks (not partitions)
                if (device.get('type') == 'disk' and 
                    device.get('tran') == 'usb' and
                    device.get('name')):
                    
                    device_info = {
                        'path': f"/dev/{device['name']}",
                        'size': self._parse_size(device.get('size', '0')),
                        'size_str': device.get('size', 'Unknown'),
                        'model': device.get('model', 'Unknown').strip(),
                        'vendor': device.get('vendor', 'Unknown').strip(),
                        'mountpoint': device.get('mountpoint'),
                        'partitions': []
                    }
                    
                    # Check for partitions
                    if 'children' in device:
                        for child in device['children']:
                            if child.get('type') == 'part':
                                partition_info = {
                                    'path': f"/dev/{child['name']}",
                                    'size': child.get('size', '0'),
                                    'mountpoint': child.get('mountpoint')
                                }
                                device_info['partitions'].append(partition_info)
                    
                    devices.append(device_info)
                    
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"Error detecting USB devices: {e}")
            # Fallback method
            devices = self._fallback_device_detection()
            
        return devices
    
    def _parse_size(self, size_str: str) -> float:
        """Parse size string to GB"""
        if not size_str:
            return 0.0
            
        # Remove any whitespace
        size_str = size_str.strip()
        
        # Extract number and unit
        match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMGT]?B?)', size_str, re.IGNORECASE)
        if not match:
            return 0.0
            
        size_num = float(match.group(1))
        unit = match.group(2).upper()
        
        # Convert to GB
        multipliers = {
            'B': 1 / (1024**3),
            'KB': 1 / (1024**2),
            'MB': 1 / 1024,
            'GB': 1,
            'TB': 1024,
            'K': 1 / (1024**2),
            'M': 1 / 1024,
            'G': 1,
            'T': 1024
        }
        
        multiplier = multipliers.get(unit, 1)
        return round(size_num * multiplier, 2)
    
    def _fallback_device_detection(self) -> List[Dict]:
        """Fallback method for device detection"""
        devices = []
        
        try:
            # Try using /proc/partitions and /sys/block
            with open('/proc/partitions', 'r') as f:
                lines = f.readlines()
                
            for line in lines[2:]:  # Skip header
                parts = line.strip().split()
                if len(parts) >= 4:
                    device_name = parts[3]
                    
                    # Only check whole disks (not partitions)
                    if re.match(r'^sd[a-z]$', device_name):
                        device_path = f"/dev/{device_name}"
                        
                        # Check if it's a USB device
                        if self._is_usb_device(device_name):
                            size_kb = int(parts[2])
                            size_gb = round(size_kb / (1024 * 1024), 2)
                            
                            device_info = {
                                'path': device_path,
                                'size': size_gb,
                                'size_str': f"{size_gb}GB",
                                'model': self._get_device_model(device_name),
                                'vendor': 'Unknown',
                                'mountpoint': None,
                                'partitions': []
                            }
                            
                            devices.append(device_info)
                            
        except Exception as e:
            print(f"Fallback device detection failed: {e}")
            
        return devices
    
    def _is_usb_device(self, device_name: str) -> bool:
        """Check if device is USB"""
        try:
            # Check if device is connected via USB
            sys_path = f"/sys/block/{device_name}"
            if os.path.exists(sys_path):
                # Follow the symlink to find the device type
                real_path = os.path.realpath(sys_path)
                return 'usb' in real_path.lower()
        except:
            pass
        return False
    
    def _get_device_model(self, device_name: str) -> str:
        """Get device model from sysfs"""
        try:
            model_path = f"/sys/block/{device_name}/device/model"
            if os.path.exists(model_path):
                with open(model_path, 'r') as f:
                    return f.read().strip()
        except:
            pass
        return "Unknown"
    
    def is_device_mounted(self, device_path: str) -> bool:
        """Check if device or any of its partitions are mounted"""
        try:
            result = subprocess.run(['mount'], capture_output=True, text=True, check=True)
            return device_path in result.stdout
        except:
            return False
    
    def get_device_partitions(self, device_path: str) -> List[str]:
        """Get list of partitions for a device"""
        partitions = []
        device_name = os.path.basename(device_path)
        
        try:
            # Look for partitions in /proc/partitions
            with open('/proc/partitions', 'r') as f:
                lines = f.readlines()
                
            for line in lines[2:]:  # Skip header
                parts = line.strip().split()
                if len(parts) >= 4:
                    partition_name = parts[3]
                    if partition_name.startswith(device_name) and partition_name != device_name:
                        partitions.append(f"/dev/{partition_name}")
                        
        except Exception as e:
            print(f"Error getting partitions: {e}")
            
        return partitions
    
    def unmount_device(self, device_path: str) -> bool:
        """Unmount device and all its partitions"""
        success = True
        
        # Get all partitions
        partitions = self.get_device_partitions(device_path)
        
        # Also try the main device
        all_paths = [device_path] + partitions
        
        for path in all_paths:
            try:
                subprocess.run(['umount', path], check=True, 
                              capture_output=True, text=True)
                print(f"Unmounted {path}")
            except subprocess.CalledProcessError:
                # It's okay if umount fails - device might not be mounted
                pass
            except Exception as e:
                print(f"Error unmounting {path}: {e}")
                success = False
                
        return success
