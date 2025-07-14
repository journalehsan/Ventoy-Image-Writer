#!/usr/bin/env python3
"""
File Operations - Handles copying ISO files to Ventoy partition
"""

import os
import shutil
import subprocess
import tempfile
from typing import List, Optional, Callable
from PySide6.QtCore import QThread, Signal

class FileCopyThread(QThread):
    """Thread for copying files to Ventoy partition"""
    
    progress_updated = Signal(int)
    status_updated = Signal(str)
    log_updated = Signal(str)
    finished_signal = Signal(bool, str)
    
    def __init__(self, images: List[str], device_path: str, progress_widget):
        super().__init__()
        self.images = images
        self.device_path = device_path
        self.progress_widget = progress_widget
        self.file_ops = FileOperations()
        
    def run(self):
        """Run the file copying operation"""
        try:
            self.log_updated.emit("Starting file copy operation...")
            
            # Find and mount Ventoy partition
            ventoy_partition = self.file_ops.get_ventoy_partition(self.device_path)
            if not ventoy_partition:
                self.finished_signal.emit(False, "Could not find Ventoy partition")
                return
            
            self.log_updated.emit(f"Found Ventoy partition: {ventoy_partition}")
            
            # Mount the partition
            mount_point = self.file_ops.mount_ventoy_partition(ventoy_partition)
            if not mount_point:
                self.finished_signal.emit(False, "Failed to mount Ventoy partition")
                return
            
            self.log_updated.emit(f"Mounted Ventoy partition at: {mount_point}")
            
            try:
                # Copy files
                total_files = len(self.images)
                
                for i, image_path in enumerate(self.images):
                    filename = os.path.basename(image_path)
                    self.status_updated.emit(f"Copying {filename}...")
                    self.log_updated.emit(f"Copying {filename} ({i+1}/{total_files})...")
                    
                    success = self.file_ops.copy_file_with_progress(
                        image_path, 
                        mount_point, 
                        self.update_file_progress
                    )
                    
                    if not success:
                        self.finished_signal.emit(False, f"Failed to copy {filename}")
                        return
                    
                    # Update overall progress
                    overall_progress = int(((i + 1) / total_files) * 100)
                    self.progress_updated.emit(overall_progress)
                    
                    self.log_updated.emit(f"Successfully copied {filename}")
                
                self.finished_signal.emit(True, f"Successfully copied {total_files} file(s)")
                
            finally:
                # Always unmount
                self.file_ops.unmount_ventoy_partition(mount_point)
                
        except Exception as e:
            self.finished_signal.emit(False, f"Error during file copy: {str(e)}")
            
    def update_file_progress(self, progress: int):
        """Update progress for current file"""
        # This could be used for per-file progress in the future
        pass

class FileOperations:
    """Handles file operations for Ventoy"""
    
    def __init__(self):
        self.temp_mount_points = []
        
    def copy_images_to_ventoy(self, images: List[str], device_path: str, progress_widget) -> None:
        """Copy images to Ventoy partition (simplified version)"""
        try:
            progress_widget.add_log("Starting file copy operation...")
            
            # Find and mount Ventoy partition
            ventoy_partition = self.get_ventoy_partition(device_path)
            if not ventoy_partition:
                progress_widget.finish_operation(False, "Could not find Ventoy partition")
                return
            
            progress_widget.add_log(f"Found Ventoy partition: {ventoy_partition}")
            
            # Mount the partition
            mount_point = self.mount_ventoy_partition(ventoy_partition)
            if not mount_point:
                progress_widget.finish_operation(False, "Failed to mount Ventoy partition")
                return
            
            progress_widget.add_log(f"Mounted Ventoy partition at: {mount_point}")
            
            try:
                # Copy files
                total_files = len(images)
                
                for i, image_path in enumerate(images):
                    filename = os.path.basename(image_path)
                    progress_widget.set_status(f"Copying {filename}...")
                    progress_widget.add_log(f"Copying {filename} ({i+1}/{total_files})...")
                    
                    success = self.copy_file_with_progress(image_path, mount_point, None)
                    
                    if not success:
                        progress_widget.finish_operation(False, f"Failed to copy {filename}")
                        return
                    
                    # Update overall progress
                    overall_progress = int(((i + 1) / total_files) * 100)
                    progress_widget.set_progress(overall_progress)
                    
                    progress_widget.add_log(f"Successfully copied {filename}")
                
                progress_widget.finish_operation(True, f"Successfully copied {total_files} file(s)")
                
            finally:
                # Always unmount
                self.unmount_ventoy_partition(mount_point)
                
        except Exception as e:
            progress_widget.finish_operation(False, f"Error during file copy: {str(e)}")
    
    def get_ventoy_partition(self, device_path: str) -> Optional[str]:
        """Get the main Ventoy partition path"""
        try:
            # Use lsblk to get partitions with labels
            result = subprocess.run([
                'lsblk', '-n', '-o', 'NAME,LABEL,SIZE', device_path
            ], capture_output=True, text=True, check=True)
            
            largest_ventoy_partition = None
            largest_size = 0
            
            for line in result.stdout.split('\n'):
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        name = parts[0]
                        label = parts[1] if len(parts) > 1 else ""
                        size_str = parts[2] if len(parts) > 2 else "0"
                        
                        # Clean up device name by removing tree-drawing characters
                        # Remove characters like ├─, └─, │, etc.
                        import re
                        clean_name = re.sub(r'[├─└│\s]+', '', name)
                        
                        print(f"Raw name: '{name}' -> Clean name: '{clean_name}'")
                        
                        # Look for Ventoy partition (not EFI)
                        if label and 'ventoy' in label.lower() and 'efi' not in label.lower():
                            # Parse size to find the largest partition
                            size = self._parse_size(size_str)
                            if size > largest_size:
                                largest_size = size
                                largest_ventoy_partition = f"/dev/{clean_name}"
                                print(f"Found Ventoy partition: {largest_ventoy_partition} (size: {size})")
            
            return largest_ventoy_partition
            
        except subprocess.CalledProcessError as e:
            print(f"Error getting Ventoy partition: {e}")
            return None
    
    def _parse_size(self, size_str: str) -> float:
        """Parse size string to bytes"""
        if not size_str:
            return 0.0
            
        size_str = size_str.strip().upper()
        
        # Extract number and unit
        import re
        match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMGT]?B?)', size_str)
        if not match:
            return 0.0
            
        size_num = float(match.group(1))
        unit = match.group(2)
        
        # Convert to bytes
        multipliers = {
            'B': 1,
            'KB': 1024,
            'MB': 1024**2,
            'GB': 1024**3,
            'TB': 1024**4,
            'K': 1024,
            'M': 1024**2,
            'G': 1024**3,
            'T': 1024**4
        }
        
        multiplier = multipliers.get(unit, 1)
        return size_num * multiplier
    
    def mount_ventoy_partition(self, partition_path: str) -> Optional[str]:
        """Mount Ventoy partition and return mount point with improved pkexec handling"""
        try:
            from PySide6.QtWidgets import QApplication
            
            # Create temporary mount point
            mount_point = tempfile.mkdtemp(prefix="ventoy_mount_")
            self.temp_mount_points.append(mount_point)
            
            print(f"Mounting {partition_path} at {mount_point}")
            
            # Process events before mount operation
            QApplication.processEvents()
            
            # Get user info for mount options
            user = os.environ.get('USER', 'user')
            uid = os.getuid()
            gid = os.getgid()
            
            # Mount the partition with improved error handling
            mount_cmd = [
                "pkexec", 
                "--disable-internal-agent",
                "env", "DISPLAY=" + os.environ.get('DISPLAY', ':0'),
                'mount', 
                '-t', 'exfat', 
                '-o', f'uid={uid},gid={gid},umask=0022',
                partition_path, 
                mount_point
            ]
            
            result = subprocess.run(
                mount_cmd, 
                capture_output=True, 
                text=True, 
                timeout=30,  # 30 second timeout
                env=dict(os.environ, DISPLAY=os.environ.get('DISPLAY', ':0'))
            )
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, mount_cmd, result.stderr)
            
            # Process events after mount
            QApplication.processEvents()
            
            # Change ownership to current user with better error handling
            user = os.environ.get('USER', 'user')
            uid = os.getuid()
            gid = os.getgid()
            
            print(f"Setting ownership of {mount_point} to {user}:{user} (uid:{uid}, gid:{gid})")
            
            # Try multiple approaches to fix permissions
            permission_fixed = False
            
            # Method 1: Use chown with pkexec
            try:
                chown_cmd = [
                    "pkexec", 
                    "--disable-internal-agent",
                    "env", "DISPLAY=" + os.environ.get('DISPLAY', ':0'),
                    "chown", 
                    "-R", 
                    f"{uid}:{gid}", 
                    mount_point
                ]
                
                chown_result = subprocess.run(
                    chown_cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=15,
                    env=dict(os.environ, DISPLAY=os.environ.get('DISPLAY', ':0'))
                )
                
                if chown_result.returncode == 0:
                    print("Successfully changed ownership using chown")
                    permission_fixed = True
                else:
                    print(f"chown failed: {chown_result.stderr}")
            except Exception as e:
                print(f"chown command failed: {e}")
            
            # Method 2: Try chmod to make it writable
            if not permission_fixed:
                try:
                    chmod_cmd = [
                        "pkexec", 
                        "--disable-internal-agent",
                        "env", "DISPLAY=" + os.environ.get('DISPLAY', ':0'),
                        "chmod", 
                        "-R", 
                        "755", 
                        mount_point
                    ]
                    
                    chmod_result = subprocess.run(
                        chmod_cmd, 
                        capture_output=True, 
                        text=True, 
                        timeout=15,
                        env=dict(os.environ, DISPLAY=os.environ.get('DISPLAY', ':0'))
                    )
                    
                    if chmod_result.returncode == 0:
                        print("Successfully set permissions using chmod")
                        permission_fixed = True
                    else:
                        print(f"chmod failed: {chmod_result.stderr}")
                except Exception as e:
                    print(f"chmod command failed: {e}")
            
            # Test write permission
            try:
                test_file = os.path.join(mount_point, '.test_write')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print("Write permission test successful")
            except Exception as e:
                print(f"Write permission test failed: {e}")
                # Try one more time with broader permissions
                try:
                    chmod_cmd = [
                        "pkexec", 
                        "--disable-internal-agent",
                        "env", "DISPLAY=" + os.environ.get('DISPLAY', ':0'),
                        "chmod", 
                        "-R", 
                        "777", 
                        mount_point
                    ]
                    
                    subprocess.run(
                        chmod_cmd, 
                        capture_output=True, 
                        text=True, 
                        timeout=15,
                        env=dict(os.environ, DISPLAY=os.environ.get('DISPLAY', ':0'))
                    )
                    print("Applied broader permissions (777)")
                except Exception as e2:
                    print(f"Final chmod attempt failed: {e2}")
            
            print(f"Successfully mounted {partition_path} at {mount_point}")
            return mount_point
            
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"Error mounting Ventoy partition: {e}")
            if mount_point in self.temp_mount_points:
                self.temp_mount_points.remove(mount_point)
            try:
                os.rmdir(mount_point)
            except:
                pass
            return None
        except Exception as e:
            print(f"Unexpected error mounting partition: {e}")
            if mount_point in self.temp_mount_points:
                self.temp_mount_points.remove(mount_point)
            try:
                os.rmdir(mount_point)
            except:
                pass
            return None
    
    def unmount_ventoy_partition(self, mount_point: str) -> bool:
        """Unmount Ventoy partition"""
        try:
            # Unmount
            subprocess.run(["pkexec", "umount", mount_point], 
                          capture_output=True, text=True, check=True)
            
            # Remove mount point
            if mount_point in self.temp_mount_points:
                self.temp_mount_points.remove(mount_point)
            
            os.rmdir(mount_point)
            return True
            
        except (subprocess.CalledProcessError, OSError) as e:
            print(f"Error unmounting Ventoy partition: {e}")
            return False
    
    def copy_file_with_progress(self, source_path: str, dest_dir: str, 
                               progress_callback: Optional[Callable] = None) -> bool:
        """Copy file to destination with progress tracking and UI responsiveness"""
        try:
            from PySide6.QtWidgets import QApplication
            import time
            
            filename = os.path.basename(source_path)
            dest_path = os.path.join(dest_dir, filename)
            
            # Check if file already exists
            if os.path.exists(dest_path):
                # Remove existing file
                os.remove(dest_path)
            
            # Get file size
            file_size = os.path.getsize(source_path)
            
            start_time = time.time()
            print(f"Starting copy of {filename} ({file_size/1024/1024:.1f}MB)...")
            
            # Copy file in chunks
            chunk_size = 1024 * 1024  # 1MB chunks
            copied = 0
            chunk_count = 0
            
            with open(source_path, 'rb') as src:
                with open(dest_path, 'wb') as dst:
                    while True:
                        chunk = src.read(chunk_size)
                        if not chunk:
                            break
                        
                        dst.write(chunk)
                        copied += len(chunk)
                        chunk_count += 1
                        
                        # Update progress callback with percentage
                        if progress_callback and file_size > 0:
                            progress = int((copied / file_size) * 100)
                            progress_callback(progress)
                        
                        # Process UI events every 10 chunks (about every 10MB)
                        if chunk_count % 10 == 0:
                            QApplication.processEvents()
                            
                        # Print progress every 100MB
                        if chunk_count % 100 == 0:
                            elapsed = int(time.time() - start_time)
                            progress_percent = int((copied / file_size) * 100)
                            print(f"Progress: {progress_percent}% ({copied/1024/1024:.1f}MB/{file_size/1024/1024:.1f}MB) - Elapsed: {elapsed}s")
            
            total_time = time.time() - start_time
            print(f"Successfully copied {filename} in {total_time:.1f} seconds")
            return True
            
        except Exception as e:
            print(f"Error copying file {source_path}: {e}")
            return False
    
    def get_available_space(self, mount_point: str) -> int:
        """Get available space in bytes"""
        try:
            stat = os.statvfs(mount_point)
            return stat.f_bavail * stat.f_frsize
        except:
            return 0
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except:
            return 0
    
    def validate_images(self, images: List[str]) -> List[str]:
        """Validate image files and return list of errors"""
        errors = []
        
        for image_path in images:
            if not os.path.exists(image_path):
                errors.append(f"File not found: {image_path}")
                continue
                
            if not os.path.isfile(image_path):
                errors.append(f"Not a file: {image_path}")
                continue
                
            # Check if it's readable
            if not os.access(image_path, os.R_OK):
                errors.append(f"File not readable: {image_path}")
                continue
                
            # Check file extension
            if not image_path.lower().endswith('.iso'):
                errors.append(f"Not an ISO file: {image_path}")
                continue
                
        return errors
    
    def cleanup(self):
        """Clean up temporary mount points"""
        for mount_point in self.temp_mount_points[:]:
            try:
                self.unmount_ventoy_partition(mount_point)
            except:
                pass
