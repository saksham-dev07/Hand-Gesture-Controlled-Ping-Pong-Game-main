import cv2
import threading
import time
from config import *
from hand_detector import HandDetector

class CameraThread:
    """Handles camera capture and MediaPipe inference in a background thread to prevent UI freezing."""
    
    def __init__(self):
        self.hand_detector = HandDetector()
        self.cap = None
        self.running = False
        self.thread = None
        
        # Thread-safe data storage
        self.lock = threading.Lock()
        self.latest_frame = None
        self.latest_hand_data = None
        self.frame_id = 0
        
    def start(self):
        """Initialize camera and start the background thread."""
        if self.running:
            return True
            
        print("📹 Initializing camera in background thread...")
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            print("❌ Camera Thread Error: Failed to open camera")
            return False
            
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, CAMERA_BUFFER_SIZE)
        
        self.hand_detector.clear_buffers()
        self.running = True
        
        # Start daemon thread so it dies when the main program exits
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()
        print("✓ Camera thread started successfully!")
        return True
        
    def stop(self):
        """Stop the background thread and release resources."""
        if not self.running:
            return
            
        print("🛑 Stopping camera thread...")
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
            
        if self.cap:
            self.cap.release()
            self.cap = None
            
        self.hand_detector.clear_buffers()
        
        with self.lock:
            self.latest_frame = None
            self.latest_hand_data = None
            
        print("✓ Camera thread stopped!")
        
    def _update_loop(self):
        """Main loop for the background thread."""
        while self.running:
            if not self.cap:
                break
                
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01) # Avoid tight loop if camera fails
                continue
                
            # Process frame with hand detector
            processed_frame, hand_data = self.hand_detector.process_frame(frame)
            
            # Update the latest data safely
            with self.lock:
                self.frame_id += 1
                self.latest_frame = processed_frame
                self.latest_hand_data = hand_data
                
    def get_latest_data(self):
        """Retrieve the latest frame and hand data instantly without blocking.
        Returns: (frame_id, frame, hand_data) or (None, None, None) if not available yet."""
        with self.lock:
            if self.latest_frame is None or self.latest_hand_data is None:
                return None, None, None
            # Return copies or references
            return self.frame_id, self.latest_frame.copy(), self.latest_hand_data.copy()
            
    def toggle_debug(self):
        self.hand_detector.toggle_debug()
        
    def close(self):
        self.stop()
        self.hand_detector.close()
