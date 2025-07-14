#!/usr/bin/env python3
"""
Ventoy Manager - Handles Ventoy download, installation and management
"""

import os
import subprocess
import tempfile
import shutil
import threading
import requests
import tarfile
from typing import Optional, Callable
from PySide6.QtCore import QObject, Signal, QThread

class VentoyInstaller(QThread):
    """Thread for installing Ventoy"""
    
    progress_updated = Signal(int)
    status_updated = Signal(str)
    log_updated = Signal(str)
    finished_signal = Signal(bool, str)
    
    def __init__(self, device_path: str, progress_widget):
        super().__init__()
        self.device_path = device_path
        self.progress_widget = progress_widget
        self.ventoy_manager = VentoyManager()
        
    def run(self):
        """Run the Ventoy installation"""
        try:
            # Download Ventoy
            self.status_updated.emit("Downloading Ventoy...")
            self.log_updated.emit("Starting Ventoy download...")
            
            ventoy_dir = self.ventoy_manager.download_ventoy(self.update_progress)
            if not ventoy_dir:
                self.finished_signal.emit(False, "Failed to download Ventoy")
                return
                
            # Install Ventoy
            self.status_updated.emit("Installing Ventoy...")
            self.log_updated.emit("Starting Ventoy installation...")
            
            success = self.ventoy_manager.install_ventoy_sync(ventoy_dir, self.device_path, self.log_updated.emit)
            
            if success:
                self.progress_updated.emit(100)
                self.finished_signal.emit(True, "Ventoy installed successfully")
            else:
                self.finished_signal.emit(False, "Ventoy installation failed")
                
        except Exception as e:
            self.finished_signal.emit(False, f"Error during installation: {str(e)}")
            
    def update_progress(self, progress: int):
        """Update progress"""
        self.progress_updated.emit(progress)

class VentoyManager:
    """Manages Ventoy download and installation"""
    
    VENTOY_VERSION = "1.1.05"
    VENTOY_URL = "https://github.com/ventoy/Ventoy/releases/download/v1.1.05/ventoy-1.1.05-linux.tar.gz"
    
    def __init__(self):
        self.ventoy_dir = None
        
    def download_ventoy(self, progress_callback: Optional[Callable] = None) -> Optional[str]:
        """Download and extract Ventoy"""
        try:
            # Create temp directory
            temp_dir = tempfile.mkdtemp(prefix="ventoy_")
            
            # Download file
            response = requests.get(self.VENTOY_URL, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            tar_path = os.path.join(temp_dir, "ventoy.tar.gz")
            
            with open(tar_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = int((downloaded / total_size) * 50)  # 50% for download
                            progress_callback(progress)
            
            # Extract archive
            if progress_callback:
                progress_callback(60)
                
            with tarfile.open(tar_path, 'r:gz') as tar:
                tar.extractall(temp_dir)
            
            # Find ventoy directory
            ventoy_dir = None
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                if os.path.isdir(item_path) and item.startswith('ventoy-'):
                    ventoy_dir = item_path
                    break
            
            if not ventoy_dir:
                raise Exception("Ventoy directory not found in archive")
            
            if progress_callback:
                progress_callback(70)
                
            self.ventoy_dir = ventoy_dir
            return ventoy_dir
            
        except Exception as e:
            print(f"Error downloading Ventoy: {e}")
            return None
    
    def download_ventoy_simple(self, progress_widget=None) -> Optional[str]:
        """Download and extract Ventoy (simplified version with progress)"""
        try:
            from PySide6.QtWidgets import QApplication
            
            # Create temp directory
            temp_dir = tempfile.mkdtemp(prefix="ventoy_")
            
            if progress_widget:
                progress_widget.add_log(f"Downloading from: {self.VENTOY_URL}")
                progress_widget.set_progress(5)
            
            # Download file with progress
            response = requests.get(self.VENTOY_URL, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            tar_path = os.path.join(temp_dir, "ventoy.tar.gz")
            
            if progress_widget:
                progress_widget.add_log(f"Downloading {total_size / (1024*1024):.1f} MB...")
            
            with open(tar_path, 'wb') as f:
                chunk_count = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        chunk_count += 1
                        
                        # Update progress and process events every 100 chunks (about every 800KB)
                        if chunk_count % 100 == 0:
                            if progress_widget and total_size > 0:
                                progress = int((downloaded / total_size) * 50) + 5  # 5-55% for download
                                progress_widget.set_progress(progress)
                            
                            # Process UI events to keep interface responsive
                            QApplication.processEvents()
            
            if progress_widget:
                progress_widget.set_progress(60)
                progress_widget.add_log("Download completed, extracting archive...")
            
            # Process events before extraction
            QApplication.processEvents()
            
            # Extract archive
            with tarfile.open(tar_path, 'r:gz') as tar:
                tar.extractall(temp_dir)
            
            if progress_widget:
                progress_widget.set_progress(65)
                progress_widget.add_log("Archive extracted successfully")
            
            # Process events after extraction
            QApplication.processEvents()
            
            # Find ventoy directory
            ventoy_dir = None
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                if os.path.isdir(item_path) and item.startswith('ventoy-'):
                    ventoy_dir = item_path
                    break
            
            if not ventoy_dir:
                raise Exception("Ventoy directory not found in archive")
            
            if progress_widget:
                progress_widget.add_log(f"Ventoy extracted to: {ventoy_dir}")
                
            self.ventoy_dir = ventoy_dir
            return ventoy_dir
            
        except Exception as e:
            print(f"Error downloading Ventoy: {e}")
            if progress_widget:
                progress_widget.add_log(f"Download error: {e}")
            return None
    
    def install_ventoy_sync(self, ventoy_dir: str, device_path: str, log_callback: Optional[Callable] = None) -> bool:
        """Install Ventoy synchronously with improved pkexec handling"""
        try:
            from PySide6.QtWidgets import QApplication
            
            # Find Ventoy2Disk.sh script
            script_path = os.path.join(ventoy_dir, "Ventoy2Disk.sh")
            if not os.path.exists(script_path):
                if log_callback:
                    log_callback("Ventoy2Disk.sh not found")
                return False
            
            # Make script executable
            os.chmod(script_path, 0o755)
            
            if log_callback:
                log_callback("Requesting administrator privileges...")
                log_callback("Please enter your password in the authentication dialog.")
            
            # Process events before running pkexec
            QApplication.processEvents()
            
            # Prepare the auto-confirmation input
            auto_confirm = "y\ny\n"  # Two "y" responses for Ventoy prompts
            
            # Run Ventoy installation with pkexec and auto-confirmation
            cmd = [
                "pkexec", 
                "--disable-internal-agent",  # Use system auth agent
                "env", "DISPLAY=" + os.environ.get('DISPLAY', ':0'),
                "bash", "-c",
                f"echo -e '{auto_confirm}' | bash {script_path} -i {device_path}"
            ]
            
            if log_callback:
                log_callback(f"Running: pkexec bash {script_path} -i {device_path} (with auto-confirmation)")
                log_callback("Automatically confirming installation prompts...")
            
            # Process events before starting subprocess
            QApplication.processEvents()
            
            # Run the command with improved error handling
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,  # Unbuffered for real-time output
                universal_newlines=True,
                env=dict(os.environ, DISPLAY=os.environ.get('DISPLAY', ':0'))
            )
            
            # Read output in real-time with UI updates
            output_lines = []
            while True:
                # Check if process is still running
                if process.poll() is not None:
                    break
                
                # Read available output
                try:
                    line = process.stdout.readline()
                    if line:
                        line = line.rstrip()
                        output_lines.append(line)
                        if log_callback:
                            log_callback(line)
                    
                    # Process UI events to keep interface responsive
                    QApplication.processEvents()
                    
                except Exception as e:
                    if log_callback:
                        log_callback(f"Output read error: {e}")
                    break
            
            # Get any remaining output
            remaining_output, error_output = process.communicate()
            if remaining_output:
                for line in remaining_output.split('\n'):
                    if line.strip():
                        if log_callback:
                            log_callback(line.strip())
            
            if error_output:
                for line in error_output.split('\n'):
                    if line.strip():
                        if log_callback:
                            log_callback(f"Error: {line.strip()}")
            
            # Check return code
            if process.returncode == 0:
                if log_callback:
                    log_callback("Ventoy installation completed successfully")
                return True
            elif process.returncode == 126:
                if log_callback:
                    log_callback("Authentication was cancelled by user")
                return False
            elif process.returncode == 127:
                if log_callback:
                    log_callback("Authentication failed - incorrect password")
                return False
            else:
                if log_callback:
                    log_callback(f"Ventoy installation failed with return code {process.returncode}")
                return False
                
        except Exception as e:
            if log_callback:
                log_callback(f"Error installing Ventoy: {e}")
            return False
    
    def install_ventoy(self, device_path: str, progress_widget) -> None:
        """Install Ventoy on device (simplified version with responsive UI)"""
        try:
            progress_widget.set_status("Downloading Ventoy...")
            progress_widget.add_log("Starting Ventoy download...")
            
            # Download Ventoy with progress updates and UI responsiveness
            ventoy_dir = self.download_ventoy_simple(progress_widget)
            if not ventoy_dir:
                progress_widget.finish_operation(False, "Failed to download Ventoy")
                return
            
            progress_widget.set_progress(70)
            progress_widget.set_status("Installing Ventoy...")
            progress_widget.add_log("Starting Ventoy installation...")
            
            # Install Ventoy
            success = self.install_ventoy_sync(ventoy_dir, device_path, progress_widget.add_log)
            
            if success:
                progress_widget.set_progress(100)
                progress_widget.finish_operation(True, "Ventoy installed successfully")
            else:
                progress_widget.finish_operation(False, "Ventoy installation failed")
                
        except Exception as e:
            progress_widget.finish_operation(False, f"Error during installation: {str(e)}")
    
    def has_ventoy(self, device_path: str) -> bool:
        """Check if device has Ventoy installed"""
        try:
            # Use lsblk to check partitions
            result = subprocess.run([
                'lsblk', '-n', '-o', 'LABEL', device_path
            ], capture_output=True, text=True, check=True)
            
            # Check if any partition has Ventoy label
            for line in result.stdout.split('\n'):
                label = line.strip()
                if label and ('ventoy' in label.lower() or 'VTOYEFI' in label):
                    return True
            
            return False
            
        except subprocess.CalledProcessError:
            return False
    
    def get_ventoy_partition(self, device_path: str) -> Optional[str]:
        """Get the main Ventoy partition path"""
        try:
            # Use lsblk to get partitions with labels
            result = subprocess.run([
                'lsblk', '-n', '-o', 'NAME,LABEL', device_path
            ], capture_output=True, text=True, check=True)
            
            for line in result.stdout.split('\n'):
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        name = parts[0]
                        label = parts[1] if len(parts) > 1 else ""
                        
                        # Strip tree formatting characters (├─, └─, etc.)
                        clean_name = name.lstrip('├─└─│ ')
                        
                        # Look for the main Ventoy partition (usually the larger one)
                        if label and 'ventoy' in label.lower() and 'efi' not in label.lower():
                            return f"/dev/{clean_name}"
            
            return None
            
        except subprocess.CalledProcessError:
            return None
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.ventoy_dir and os.path.exists(self.ventoy_dir):
            try:
                # Remove the parent temp directory
                temp_parent = os.path.dirname(self.ventoy_dir)
                if temp_parent.startswith('/tmp/'):
                    shutil.rmtree(temp_parent)
            except Exception as e:
                print(f"Error cleaning up: {e}")
    
    def get_ventoy_info(self, device_path: str) -> dict:
        """Get Ventoy information from device"""
        info = {
            'installed': False,
            'version': None,
            'partitions': []
        }
        
        try:
            if self.has_ventoy(device_path):
                info['installed'] = True
                
                # Get partition information
                result = subprocess.run([
                    'lsblk', '-n', '-o', 'NAME,SIZE,LABEL,TYPE', device_path
                ], capture_output=True, text=True, check=True)
                
                for line in result.stdout.split('\n'):
                    if line.strip():
                        parts = line.strip().split()
                        if len(parts) >= 3 and parts[3] == 'part':
                            # Strip tree formatting characters (├─, └─, etc.)
                            clean_name = parts[0].lstrip('├─└─│ ')
                            partition_info = {
                                'name': clean_name,
                                'size': parts[1],
                                'label': parts[2] if len(parts) > 2 else '',
                                'path': f"/dev/{clean_name}"
                            }
                            info['partitions'].append(partition_info)
            
        except Exception as e:
            print(f"Error getting Ventoy info: {e}")
            
        return info
