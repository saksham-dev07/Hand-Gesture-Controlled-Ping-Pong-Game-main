"""
Hand Gesture Controlled Ping Pong Game
Main application file that orchestrates all modules

OPTIMIZED: CPU-only version with all GPU code removed
Refactored into modular components:
- config.py: All constants and configuration
- hand_detector.py: Hand detection and gesture recognition
- game_objects.py: Ball and Paddle classes
- game_engine.py: Game logic and physics
- ui_manager.py: User interface management
"""

import cv2
import tkinter as tk
import customtkinter as ctk
import time
import sys
from collections import deque

# Import game modules
from config import *
from camera_thread import CameraThread
from game_engine import GameEngine
from ui_manager import UIManager


class HandPongGame:
    """Main game application that coordinates all components"""
    
    def __init__(self):
        """Initialize the game"""
        print("🚀 Initializing Hand Pong Game...")
        
        # Initialize components (CPU-only, no GPU checks)
        self.camera_thread = CameraThread()
        self.game_engine = GameEngine()
        
        # Camera tracking
        self.frame_count = 0
        self.last_processed_frame_id = -1
        
        # Game state
        self.app_state = STATE_MENU
        self.game_running = False
        self.gesture_pause_enabled = True
        self.countdown_seconds = CALIBRATION_COUNTDOWN_SECONDS
        
        # Gesture cooldown to prevent spam
        self.last_thumbs_up_time = 0
        self.last_thumbs_down_time = 0
        self.gesture_cooldown = 1.0  # seconds between gesture activations
        
        # Performance tracking
        self.fps_counter = deque(maxlen=FPS_BUFFER_SIZE)
        self.last_frame_time = time.time()
        self.current_fps = 0
        
        # Setup UI
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.root = ctk.CTk()
        self.ui_manager = UIManager(self.root)
        
        # Bind button commands
        self.ui_manager.start_stop_button.configure(command=self.toggle_game)
        self.ui_manager.pause_button.configure(command=self.toggle_pause)
        self.ui_manager.quit_button.configure(command=self.quit_game)
        self.ui_manager.mode_selector.configure(command=self.on_mode_changed)
        
        # Bind keyboard shortcuts
        self.root.bind('<F11>', lambda e: self.ui_manager.toggle_fullscreen())
        self.root.bind('<Escape>', lambda e: self.ui_manager.exit_fullscreen())
        self.root.bind('d', lambda e: self.camera_thread.toggle_debug())
        self.root.bind('D', lambda e: self.camera_thread.toggle_debug())
        
        # Initialize display to Main Menu
        self.ui_manager.draw_main_menu(self.game_engine.game_mode)
        
        # Show welcome message after UI loads
        self.root.after(1000, self.ui_manager.show_welcome_message)
        
        print("✓ Game initialized successfully!")
    
    def on_mode_changed(self, value):
        """Handle mode selection change from UI"""
        mode = MODE_1PLAYER if "1-Player" in value else MODE_2PLAYER
        self.game_engine.set_game_mode(mode)
        if self.app_state == STATE_MENU:
            self.ui_manager.draw_main_menu(mode)

    def toggle_game(self):
        """Toggle match on/off"""
        if not self.game_running:
            self.start_game()
        else:
            self.stop_game()
    
    def toggle_pause(self):
        """Toggle game pause"""
        if not self.game_running or self.app_state != STATE_PLAYING:
            return
        
        is_paused = self.game_engine.toggle_pause()
        self.ui_manager.update_pause_button(is_paused)
        
        if is_paused:
            print("⏸️ Game paused")
        else:
            print("▶️ Game resumed")
    
    def start_game(self):
        """Start the calibration countdown phase & camera"""
        print("🎮 Starting Hand Pong Match...")
        
        try:
            # Initialize camera thread
            print("📹 Initializing camera background thread...")
            if not self.camera_thread.start():
                self.ui_manager.show_error("📹 Camera Error", CAMERA_ERROR_MESSAGE)
                return
            
            # Update state to CALIBRATING
            self.game_running = True
            self.app_state = STATE_CALIBRATING
            self.countdown_seconds = CALIBRATION_COUNTDOWN_SECONDS
            self.game_engine.reset()
            
            # Update UI
            self.ui_manager.update_start_stop_button(True)
            self.ui_manager.update_camera_status(True)
            
            # Start game loop and countdown timer
            self.game_loop()
            self.root.after(1000, self.tick_countdown)
            
            print("✓ Camera initialized! Starting 3s Calibration Countdown...")
            
        except Exception as e:
            print(f"❌ Error starting match: {e}")
            self.ui_manager.show_error("Error", f"Failed to start match:\n{str(e)}")

    def tick_countdown(self):
        """Tick down the 3-second calibration timer"""
        if not self.game_running or self.app_state != STATE_CALIBRATING:
            return
        
        self.countdown_seconds -= 1
        if self.countdown_seconds <= 0:
            self.app_state = STATE_PLAYING
            print("🚀 COUNTDOWN COMPLETE - MATCH STARTED!")
        else:
            self.root.after(1000, self.tick_countdown)
    
    def stop_game(self):
        """Stop match and return to Main Menu"""
        print("🛑 Returning to Main Menu...")
        
        self.game_running = False
        self.app_state = STATE_MENU
        
        # Stop camera thread
        self.camera_thread.stop()
        
        # Update UI
        self.ui_manager.update_start_stop_button(False)
        self.ui_manager.update_camera_status(False)
        self.ui_manager.update_hand_status(False, False)
        self.ui_manager.clear_camera_preview()
        self.ui_manager.draw_main_menu(self.game_engine.game_mode)
        
        print("✓ Stopped match and returned to menu!")
    
    def game_loop(self):
        """Main application loop"""
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
            
            # Fetch latest camera data once per game loop tick
            frame_id, processed_frame, hand_data = self.camera_thread.get_latest_data()
            
            # Process camera UI and gestures ONLY if we received a totally new frame from the background thread
            is_new_frame = (frame_id is not None and frame_id != self.last_processed_frame_id)
            if is_new_frame:
                self.last_processed_frame_id = frame_id
                self.process_camera(processed_frame, hand_data)
            
            # Update game physics ONLY when state is PLAYING and not paused
            if self.app_state == STATE_PLAYING and not self.game_engine.is_paused():
                left_paddle_y = None
                right_paddle_y = None
                left_detected = False
                right_detected = False
                
                if hand_data:
                    left_detected = hand_data.get('left_detected', False)
                    right_detected = hand_data.get('right_detected', False)
                    if left_detected:
                        left_paddle_y = hand_data.get('left_paddle_y')
                    if right_detected:
                        right_paddle_y = hand_data.get('right_paddle_y')
                
                left_hand_data = {
                    'detected': left_detected,
                    'paddle_y': left_paddle_y
                }
                right_hand_data = {
                    'detected': right_detected,
                    'paddle_y': right_paddle_y
                }
                
                # Update game engine
                self.game_engine.update(left_hand_data, right_hand_data)
            
            # Update display
            self.update_display(hand_data)
            
        except Exception as e:
            print(f"⚠️ Game loop error: {e}")
            import traceback
            traceback.print_exc()
        
        # Continue loop at target FPS
        self.root.after(TARGET_FRAME_TIME, self.game_loop)
    
    def process_camera(self, processed_frame, hand_data):
        """Process gestures and camera preview for a completely new frame"""
        self.frame_count += 1
        
        # Handle gesture pause/resume only when match is actively playing
        if self.gesture_pause_enabled and self.app_state == STATE_PLAYING:
            # PAUSE when both fists are detected
            if hand_data['both_fists_just_detected']:
                if not self.game_engine.is_paused():
                    self.game_engine.set_pause(True)
                    self.ui_manager.update_pause_button(True)
                    print("✊✊ Both fists detected - PAUSED!")
            
            # RESUME when both hands are open
            elif hand_data.get('both_hands_just_opened', False):
                if self.game_engine.is_paused():
                    self.game_engine.set_pause(False)
                    self.ui_manager.update_pause_button(False)
                    print("👐👐 Both hands open - RESUMED!")
        
        # Handle thumbs up/down for ball speed control (with cooldown)
        if self.app_state == STATE_PLAYING:
            current_time = time.time()
            if hand_data.get('thumbs_up', False):
                if current_time - self.last_thumbs_up_time > self.gesture_cooldown:
                    self.game_engine.increase_ball_speed()
                    self.last_thumbs_up_time = current_time
            
            if hand_data.get('thumbs_down', False):
                if current_time - self.last_thumbs_down_time > self.gesture_cooldown:
                    self.game_engine.decrease_ball_speed()
                    self.last_thumbs_down_time = current_time
        
        # Update camera preview
        if self.frame_count % CAMERA_PREVIEW_UPDATE_FREQ == 0:
            paused = (self.app_state == STATE_PLAYING and self.game_engine.is_paused() and hand_data['both_fists'])
            self.ui_manager.update_camera_preview(processed_frame, paused)
    
    def update_display(self, hand_data):
        """Update all display elements based on application state"""
        left_detected = False
        right_detected = False
        if hand_data:
            left_detected = hand_data.get('left_detected', False)
            right_detected = hand_data.get('right_detected', False)
            
        # Update hand status
        self.ui_manager.update_hand_status(left_detected, right_detected)
        
        # Update score
        self.ui_manager.update_score(self.game_engine.get_score())
        
        # Update FPS
        if self.frame_count % FPS_DISPLAY_UPDATE_FREQ == 0:
            self.ui_manager.update_fps(self.current_fps)
        
        # Render canvas according to App State
        if self.app_state == STATE_MENU:
            self.ui_manager.draw_main_menu(self.game_engine.game_mode)
        elif self.app_state == STATE_CALIBRATING:
            self.ui_manager.draw_calibration_overlay(
                self.countdown_seconds,
                left_detected,
                right_detected,
                self.game_engine.game_mode
            )
        elif self.app_state == STATE_PLAYING:
            self.ui_manager.draw_game(self.game_engine.get_game_state())
    
    def quit_game(self):
        """Quit the application"""
        print("🛑 Quitting Hand Pong Game...")
        
        if self.game_running:
            self.stop_game()
        
        # Clean up resources
        self.camera_thread.close()
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
        # Fix Windows console emoji printing error
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
            
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