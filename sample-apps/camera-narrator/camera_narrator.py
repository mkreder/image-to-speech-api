#!/usr/bin/env python3
"""
Camera Narrator - Continuous Image Description with Audio Playback

This application captures images from a USB camera, sends them to the 
image description API, and plays back audio descriptions.

Requirements:
- opencv-python
- requests
- pygame
- pillow

Install with: pip install opencv-python requests pygame pillow
"""

import cv2
import base64
import requests
import json
import time
import pygame
import io
import threading
from PIL import Image
import argparse
import sys

class CameraNarrator:
    def __init__(self, api_endpoint, capture_interval=5, voice="Joanna", language="en"):
        """
        Initialize the Camera Narrator
        
        Args:
            api_endpoint (str): The API endpoint URL
            capture_interval (int): Seconds between captures
            voice (str): Amazon Polly voice to use
            language (str): Language code for descriptions
        """
        self.api_endpoint = api_endpoint.rstrip('/')
        self.capture_interval = capture_interval
        self.voice = voice
        self.language = language
        self.camera = None
        self.running = False
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        print(f"Camera Narrator initialized:")
        print(f"  API Endpoint: {self.api_endpoint}")
        print(f"  Capture Interval: {capture_interval} seconds")
        print(f"  Voice: {voice}")
        print(f"  Language: {language}")
    
    def initialize_camera(self, camera_index=0):
        """Initialize the USB camera"""
        try:
            self.camera = cv2.VideoCapture(camera_index)
            if not self.camera.isOpened():
                raise Exception(f"Could not open camera at index {camera_index}")
            
            # Set camera properties for better quality
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            print("Camera initialized successfully")
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def capture_image(self):
        """Capture an image from the camera and return as base64"""
        if not self.camera or not self.camera.isOpened():
            raise Exception("Camera not initialized")
        
        ret, frame = self.camera.read()
        if not ret:
            raise Exception("Failed to capture image from camera")
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(frame_rgb)
        
        # Convert to base64
        buffer = io.BytesIO()
        pil_image.save(buffer, format='JPEG', quality=85)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return image_base64, frame
    
    def get_audio_description(self, image_base64):
        """Send image to API and get audio description"""
        try:
            payload = {
                "image": image_base64,
                "voice": self.voice,
                "language": self.language
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            print("Sending image to API for description...")
            response = requests.post(
                f"{self.api_endpoint}/describe/audio",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('description'), result.get('audio')
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None, None
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None, None
        except Exception as e:
            print(f"Error getting audio description: {e}")
            return None, None
    
    def play_audio(self, audio_base64):
        """Play audio from base64 encoded MP3 data"""
        try:
            # Decode base64 audio
            audio_data = base64.b64decode(audio_base64)
            
            # Create a BytesIO object
            audio_buffer = io.BytesIO(audio_data)
            
            # Load and play the audio
            pygame.mixer.music.load(audio_buffer)
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def display_frame(self, frame, description=None):
        """Display the current frame with optional description overlay"""
        display_frame = frame.copy()
        
        if description:
            # Add text overlay
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            color = (0, 255, 0)  # Green
            thickness = 2
            
            # Split long descriptions into multiple lines
            words = description.split()
            lines = []
            current_line = ""
            max_width = 80  # characters per line
            
            for word in words:
                if len(current_line + " " + word) <= max_width:
                    current_line += " " + word if current_line else word
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            # Draw text lines
            y_offset = 30
            for line in lines[:5]:  # Limit to 5 lines
                cv2.putText(display_frame, line, (10, y_offset), 
                           font, font_scale, color, thickness)
                y_offset += 25
        
        # Add status text
        status_text = f"Next capture in: {self.capture_interval}s | Press 'q' to quit"
        cv2.putText(display_frame, status_text, (10, display_frame.shape[0] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow('Camera Narrator', display_frame)
    
    def run(self):
        """Main application loop"""
        if not self.initialize_camera():
            return False
        
        self.running = True
        last_capture_time = 0
        current_description = None
        
        print("\nStarting Camera Narrator...")
        print("Press 'q' in the camera window to quit")
        print("Press 'c' to capture immediately")
        print("-" * 50)
        
        try:
            while self.running:
                # Capture and display current frame
                try:
                    ret, frame = self.camera.read()
                    if not ret:
                        print("Failed to read from camera")
                        break
                    
                    # Check if it's time for a new capture
                    current_time = time.time()
                    if current_time - last_capture_time >= self.capture_interval:
                        # Capture and process in a separate thread to avoid blocking
                        threading.Thread(
                            target=self.process_image_async,
                            args=(frame.copy(),),
                            daemon=True
                        ).start()
                        last_capture_time = current_time
                    
                    # Display frame
                    self.display_frame(frame, current_description)
                    
                    # Handle keyboard input
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        print("Quit requested by user")
                        break
                    elif key == ord('c'):
                        # Immediate capture
                        threading.Thread(
                            target=self.process_image_async,
                            args=(frame.copy(),),
                            daemon=True
                        ).start()
                        last_capture_time = current_time
                
                except Exception as e:
                    print(f"Error in main loop: {e}")
                    time.sleep(1)
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        finally:
            self.cleanup()
        
        return True
    
    def process_image_async(self, frame):
        """Process image asynchronously to avoid blocking the main loop"""
        try:
            # Convert frame to base64
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG', quality=85)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Get description and audio
            description, audio_base64 = self.get_audio_description(image_base64)
            
            if description and audio_base64:
                print(f"Description: {description}")
                
                # Play audio
                self.play_audio(audio_base64)
                
                # Update current description for display
                global current_description
                current_description = description
            
        except Exception as e:
            print(f"Error processing image: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        
        if self.camera:
            self.camera.release()
        
        cv2.destroyAllWindows()
        pygame.mixer.quit()
        
        print("Cleanup completed")

def main():
    parser = argparse.ArgumentParser(description='Camera Narrator - AI-powered image descriptions with audio')
    parser.add_argument('api_endpoint', help='API endpoint URL (e.g., https://your-api.execute-api.us-east-1.amazonaws.com/Prod)')
    parser.add_argument('--interval', '-i', type=int, default=5, help='Capture interval in seconds (default: 5)')
    parser.add_argument('--voice', '-v', default='Joanna', help='Amazon Polly voice (default: Joanna)')
    parser.add_argument('--language', '-l', default='en', help='Language code (default: en)')
    parser.add_argument('--camera', '-c', type=int, default=0, help='Camera index (default: 0)')
    
    args = parser.parse_args()
    
    # Validate API endpoint
    if not args.api_endpoint.startswith('http'):
        print("Error: API endpoint must start with http:// or https://")
        sys.exit(1)
    
    # Create and run the narrator
    narrator = CameraNarrator(
        api_endpoint=args.api_endpoint,
        capture_interval=args.interval,
        voice=args.voice,
        language=args.language
    )
    
    success = narrator.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
