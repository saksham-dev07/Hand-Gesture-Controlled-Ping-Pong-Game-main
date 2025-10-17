"""
Hand Gesture Controlled Ping Pong Game
Main application file that orchestrates all modules

Refactored into modular components:
- config.py: All constants and configuration
- hand_detector.py: Hand detection and gesture recognition
- game_objects.py: Ball and Paddle classes
- game_engine.py: Game logic and physics
- ui_manager.py: User interface management
"""

import cv2
import tkinter as tk
import time
from collections import deque

# Import game modules
from config import *
from hand_detector import HandDetector
from game_engine import GameEngine
from ui_manager import UIManager


class HandPongGame:
    """Main game application that coordinates all components"""
    
    def __init__(self):
        """Initialize the game"""
        print("🚀 Initializing Hand Pong Game...")
        
        # Check for GPU support
        self.use_gpu = HandDetector.check_gpu_support()
        
        # Initialize components
        self.hand_detector = HandDetector(use_gpu=self.use_gpu)
        self.game_engine = GameEngine()
        
        # Camera
        self.cap = None
        self.frame_count = 0
        
        # Game state
        self.game_running = False
        self.gesture_pause_enabled = True
        
        # Performance tracking
        self.fps_counter = deque(maxlen=FPS_BUFFER_SIZE)
        self.last_frame_time = time.time()
        self.current_fps = 0
        
        # Setup UI
        self.root = tk.Tk()
        self.ui_manager = UIManager(self.root, use_gpu=self.use_gpu)
        
        # Bind button commands
        self.ui_manager.start_stop_button.config(command=self.toggle_game)
        self.ui_manager.pause_button.config(command=self.toggle_pause)
        self.ui_manager.quit_button.config(command=self.quit_game)
        
        # Bind keyboard shortcuts
        self.root.bind('<F11>', lambda e: self.ui_manager.toggle_fullscreen())
        self.root.bind('<Escape>', lambda e: self.ui_manager.exit_fullscreen())
        self.root.bind('d', lambda e: self.hand_detector.toggle_debug())
        self.root.bind('D', lambda e: self.hand_detector.toggle_debug())
        
        # Initialize display
        self.ui_manager.draw_game(self.game_engine.get_game_state())
        
        # Show welcome message after UI loads
        self.root.after(1000, self.ui_manager.show_welcome_message)
        
        print("✓ Game initialized successfully!")
    
    def toggle_game(self):
        """Toggle game on/off"""
        if not self.game_running:
            self.start_game()
        else:
            self.stop_game()
    
    def toggle_pause(self):
        """Toggle game pause"""
        if not self.game_running:
            return
        
        is_paused = self.game_engine.toggle_pause()
        self.ui_manager.update_pause_button(is_paused)
        
        if is_paused:
            print("⏸️ Game paused")
        else:
            print("▶️ Game resumed")
    
    def start_game(self):
        """Start the game and camera"""
        print("🎮 Starting Hand Pong Game...")
        
        try:
            # Initialize camera
            print("📹 Initializing camera...")
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                self.ui_manager.show_error("📹 Camera Error", CAMERA_ERROR_MESSAGE)
                return
            
            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, CAMERA_BUFFER_SIZE)
            
            # Update game state
            self.game_running = True
            self.game_engine.reset()
            self.hand_detector.clear_buffers()
            
            # Update UI
            self.ui_manager.update_start_stop_button(True)
            self.ui_manager.update_camera_status(True)
            
            # Start game loop
            self.game_loop()
            
            print("✓ Game started successfully!")
            print("✋ Show your hands to the camera to control the paddles!")
            
        except Exception as e:
            print(f"❌ Error starting game: {e}")
            self.ui_manager.show_error("Error", f"Failed to start game:\n{str(e)}")
    
    def stop_game(self):
        """Stop the game and camera"""
        print("🛑 Stopping game...")
        
        self.game_running = False
        
        # Release camera
        if self.cap:
            self.cap.release()
            self.cap = None
        
        # Clear buffers
        self.hand_detector.clear_buffers()
        
        # Update UI
        self.ui_manager.update_start_stop_button(False)
        self.ui_manager.update_camera_status(False)
        self.ui_manager.update_hand_status(False, False)
        self.ui_manager.clear_camera_preview()
        
        print("✓ Game stopped!")
    
    def game_loop(self):
        """Main game loop"""
        if not self.game_running:
            return
        
        try:
            # Calculate FPS
            current_time = time.time()
            delta_time = current_time - self.last_frame_time
            self.last_frame_time = current_time
            
            if delta_time > 0:
                fps = 1.0 / delta_time
                self.fps_counter.append(fps)
                self.current_fps = sum(self.fps_counter) / len(self.fps_counter)
            
            # Process camera and hands
            self.process_camera()
            
            # Update game physics (only if not paused)
            if not self.game_engine.is_paused():
                # Get hand data
                left_hand_data = {
                    'detected': self.hand_detector.left_hand_detected,
                    'paddle_y': None
                }
                right_hand_data = {
                    'detected': self.hand_detector.right_hand_detected,
                    'paddle_y': None
                }
                
                # Update with actual paddle positions if hands detected
                # (Hand detector processes this internally)
                
                # Update game engine
                self.game_engine.update(left_hand_data, right_hand_data)
            
            # Update display
            self.update_display()
            
        except Exception as e:
            print(f"⚠️ Game loop error: {e}")
            import traceback
            traceback.print_exc()
        
        # Continue loop at target FPS
        self.root.after(TARGET_FRAME_TIME, self.game_loop)
    
    def process_camera(self):
        """Process camera frame and detect hands"""
        if not self.cap:
            return
        
        ret, frame = self.cap.read()
        if not ret:
            print("⚠️ Failed to read camera frame")
            return
        
        self.frame_count += 1
        
        # Process frame with hand detector
        processed_frame, hand_data = self.hand_detector.process_frame(frame)
        
        # Update paddles based on hand data
        if hand_data['left_detected'] and hand_data['left_paddle_y'] is not None:
            self.game_engine.update_paddle_from_hand(1, hand_data['left_paddle_y'])
        
        if hand_data['right_detected'] and hand_data['right_paddle_y'] is not None:
            self.game_engine.update_paddle_from_hand(2, hand_data['right_paddle_y'])
        
        # Handle gesture pause
        if self.gesture_pause_enabled and hand_data['both_fists_just_detected']:
            is_paused = self.game_engine.toggle_pause()
            self.ui_manager.update_pause_button(is_paused)
            if is_paused:
                print("✊✊ Both fists detected - PAUSED!")
            else:
                print("👐👐 Hands open - RESUMED!")
        
        # Update camera preview (less frequently)
        if self.frame_count % CAMERA_PREVIEW_UPDATE_FREQ == 0:
            paused = self.game_engine.is_paused() and hand_data['both_fists']
            self.ui_manager.update_camera_preview(processed_frame, self.use_gpu, paused)
    
    def update_display(self):
        """Update all display elements"""
        # Update hand status
        self.ui_manager.update_hand_status(
            self.hand_detector.left_hand_detected,
            self.hand_detector.right_hand_detected
        )
        
        # Update score
        self.ui_manager.update_score(self.game_engine.get_score())
        
        # Update FPS (less frequently)
        if self.frame_count % FPS_DISPLAY_UPDATE_FREQ == 0:
            self.ui_manager.update_fps(self.current_fps)
        
        # Draw game state
        self.ui_manager.draw_game(self.game_engine.get_game_state())
    
    def quit_game(self):
        """Quit the application"""
        print("🛑 Quitting Hand Pong Game...")
        
        if self.game_running:
            self.stop_game()
        
        # Clean up resources
        if self.cap:
            self.cap.release()
        
        self.hand_detector.close()
        cv2.destroyAllWindows()
        
        self.root.quit()
        self.root.destroy()
        print("✓ Game closed successfully!")
    
    def run(self):
        """Run the game"""
        self.root.protocol("WM_DELETE_WINDOW", self.quit_game)
        print("🎮 Hand Pong Game is ready!")
        print("📱 This is a Python Desktop Application")
        print("👀 Look for the game window with the START GAME button!")
        self.root.mainloop()


if __name__ == "__main__":
    try:
        print("🚀 Launching Hand Pong Game...")
        print("📱 This runs as a Python Desktop Application (not in browser)")
        print("=" * 60)
        game = HandPongGame()
        game.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print(f"\n{DEPENDENCIES_MESSAGE}")
        input("\nPress Enter to exit...")
