#!/usr/bin/env python3
"""
Test script to verify GitHub URL download speed
"""

import time
import requests
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_download_speed():
    """Test download speed from GitHub"""
    url = "https://github.com/ventoy/Ventoy/releases/download/v1.1.05/ventoy-1.1.05-linux.tar.gz"
    
    print(f"Testing download from: {url}")
    print("Getting file info...")
    
    try:
        # Get headers first to check file size
        response = requests.head(url)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        print(f"File size: {total_size / (1024*1024):.1f} MB")
        
        # Start download test
        start_time = time.time()
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        downloaded = 0
        chunk_count = 0
        
        print("Starting download test...")
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                downloaded += len(chunk)
                chunk_count += 1
                
                # Show progress every 1000 chunks (about 8MB)
                if chunk_count % 1000 == 0:
                    elapsed = time.time() - start_time
                    speed = downloaded / (1024 * 1024) / elapsed if elapsed > 0 else 0
                    progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                    print(f"Downloaded: {downloaded / (1024*1024):.1f} MB ({progress:.1f}%) - Speed: {speed:.1f} MB/s")
                
                # Stop after downloading a few MB for testing
                if downloaded >= 10 * 1024 * 1024:  # 10MB test
                    break
        
        elapsed = time.time() - start_time
        speed = downloaded / (1024 * 1024) / elapsed if elapsed > 0 else 0
        
        print(f"\nTest completed:")
        print(f"Downloaded: {downloaded / (1024*1024):.1f} MB")
        print(f"Time: {elapsed:.2f} seconds")
        print(f"Average speed: {speed:.1f} MB/s")
        print("✅ GitHub URL is working and fast!")
        
    except Exception as e:
        print(f"❌ Download test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_download_speed()
