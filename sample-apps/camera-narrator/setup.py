#!/usr/bin/env python3
"""
Setup script for Camera Narrator
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def check_camera():
    """Check if camera is available"""
    print("Checking camera availability...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print("✅ Camera is working!")
                return True
            else:
                print("⚠️  Camera detected but unable to capture frames")
                return False
        else:
            print("❌ No camera detected at index 0")
            return False
    except ImportError:
        print("❌ OpenCV not installed")
        return False
    except Exception as e:
        print(f"❌ Error checking camera: {e}")
        return False

def main():
    print("Camera Narrator Setup")
    print("=" * 30)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Check camera
    if not check_camera():
        print("\n⚠️  Camera check failed. You may need to:")
        print("   - Connect a USB camera")
        print("   - Grant camera permissions")
        print("   - Try a different camera index")
    
    print("\n🎉 Setup complete!")
    print("\nUsage:")
    print("python camera_narrator.py YOUR_API_ENDPOINT")
    print("\nExample:")
    print("python camera_narrator.py https://your-api.execute-api.us-east-1.amazonaws.com/Prod")
    print("\nOptions:")
    print("  --interval 10    # Capture every 10 seconds")
    print("  --voice Matthew  # Use Matthew voice")
    print("  --language es    # Spanish descriptions")

if __name__ == "__main__":
    main()
