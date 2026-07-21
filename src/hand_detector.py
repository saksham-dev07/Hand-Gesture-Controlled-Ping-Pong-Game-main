"""
Hand Detection Module
Handles MediaPipe hand detection, tracking, and gesture recognition
OPTIMIZED: CPU-only version with modern MediaPipe Tasks API (GestureRecognizer)
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
from collections import deque
from config import *
import time

class HandDetector:
    """Handles hand detection and gesture recognition using MediaPipe"""
    
    def __init__(self):
        """Initialize the hand detector"""
        print("💻 Using optimized CPU mode for hand detection (Tasks API GestureRecognizer)")
        
        # Initialize MediaPipe Tasks API
        base_options = python.BaseOptions(model_asset_path='assets/gesture_recognizer.task')
        options = vision.GestureRecognizerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=MAX_NUM_HANDS,
            min_hand_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_hand_presence_confidence=MIN_TRACKING_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE
        )
        self.detector = vision.GestureRecognizer.create_from_options(options)
        
        self.HAND_CONNECTIONS = [
            (0, 1), (1, 2), (2, 3), (3, 4), # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8), # Index
            (5, 9), (9, 10), (10, 11), (11, 12), # Middle
            (9, 13), (13, 14), (14, 15), (15, 16), # Ring
            (13, 17), (0, 17), (17, 18), (18, 19), (19, 20) # Pinky
        ]
        
        # Hand tracking state
        self.left_hand_detected = False
        self.right_hand_detected = False
        self.left_hand_fist = False
        self.right_hand_fist = False
        self.both_fists_detected = False
        self.both_hands_open = False  # Track when both hands are open
        self.left_hand_open = False
        self.right_hand_open = False
        
        # Thumbs up/down detection
        self.thumbs_up_detected = False
        self.thumbs_down_detected = False
        
        # Hand position smoothing
        self.left_hand_positions = deque(maxlen=HAND_POSITION_BUFFER_SIZE)
        self.right_hand_positions = deque(maxlen=HAND_POSITION_BUFFER_SIZE)
        
        # Exponential smoothing for stable paddle movement
        self.left_hand_smoothed_y = None
        self.right_hand_smoothed_y = None
        
        # Debug mode
        self.debug_fist_detection = False
        
        # Frame counting for optimization
        self.frame_count = 0
    
    def toggle_debug(self):
        """Toggle debug mode for fist detection"""
        self.debug_fist_detection = not self.debug_fist_detection
        
        if self.debug_fist_detection:
            print("\n" + "="*60)
            print("🔍 DEBUG MODE ENABLED")
            print("="*60 + "\n")
        else:
            print("\n" + "="*60)
            print("🔍 DEBUG MODE DISABLED")
            print("="*60 + "\n")
    
    def _draw_landmarks(self, frame, landmarks, color, connection_color, w, h):
        """Manually draw landmarks since mp.solutions is removed"""
        for connection in self.HAND_CONNECTIONS:
            start_idx, end_idx = connection
            start_pt, end_pt = landmarks[start_idx], landmarks[end_idx]
            
            x1, y1 = int(start_pt.x * w), int(start_pt.y * h)
            x2, y2 = int(end_pt.x * w), int(end_pt.y * h)
            cv2.line(frame, (x1, y1), (x2, y2), connection_color, 2)
            
        for pt in landmarks:
            x, y = int(pt.x * w), int(pt.y * h)
            cv2.circle(frame, (x, y), 3, color, -1)
            
    def process_frame(self, frame):
        """
        Process a camera frame and detect hands
        Returns: (processed_frame, hand_data)
        """
        self.frame_count += 1
        
        frame = cv2.flip(frame, 1)
        
        if self.frame_count % FRAME_SKIP == 0:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            results = self.detector.recognize(mp_image)
            
            self.left_hand_detected = False
            self.right_hand_detected = False
            self.left_hand_fist = False
            self.right_hand_fist = False
            self.left_hand_open = False
            self.right_hand_open = False
            self.thumbs_up_detected = False
            self.thumbs_down_detected = False
            
            left_paddle_y = None
            right_paddle_y = None
            
            if results.hand_landmarks and results.handedness:
                h, w, _ = frame.shape
                screen_center = w / 2
                
                for idx in range(len(results.hand_landmarks)):
                    landmarks = results.hand_landmarks[idx]
                    category = results.handedness[idx][0]
                    hand_label = category.category_name
                    confidence = category.score
                    
                    if confidence < HAND_CONFIDENCE_THRESHOLD:
                        continue
                        
                    # Get gesture
                    gesture_name = "None"
                    if results.gestures and len(results.gestures) > idx and len(results.gestures[idx]) > 0:
                        gesture_category = results.gestures[idx][0]
                        if gesture_category.score > 0.5:
                            gesture_name = gesture_category.category_name
                            
                    is_fist_gesture = (gesture_name == "Closed_Fist")
                    is_thumbs_up_gesture = (gesture_name == "Thumb_Up")
                    is_thumbs_down_gesture = (gesture_name == "Thumb_Down")
                    is_open_palm = (gesture_name == "Open_Palm")
                    
                    if is_thumbs_up_gesture:
                        self.thumbs_up_detected = True
                    if is_thumbs_down_gesture:
                        self.thumbs_down_detected = True
                    
                    if self.debug_fist_detection:
                        print(f"\n{'='*50}")
                        print(f"🖐️ Analyzing hand (confidence: {confidence:.2f}) -> Gesture: {gesture_name}")
                    
                    middle_finger = landmarks[12]
                    hand_x = middle_finger.x * w
                    hand_y = middle_finger.y * h
                    paddle_y_normalized = hand_y / h
                    
                    if hand_x < screen_center:
                        self.left_hand_detected = True
                        self.left_hand_fist = is_fist_gesture
                        self.left_hand_open = is_open_palm
                        self.left_hand_positions.append(paddle_y_normalized)
                        
                        if self.left_hand_smoothed_y is None:
                            self.left_hand_smoothed_y = paddle_y_normalized
                        else:
                            self.left_hand_smoothed_y = (HAND_POSITION_SMOOTHING_FACTOR * paddle_y_normalized + 
                                                         (1 - HAND_POSITION_SMOOTHING_FACTOR) * self.left_hand_smoothed_y)
                        left_paddle_y = self.left_hand_smoothed_y
                    else:
                        self.right_hand_detected = True
                        self.right_hand_fist = is_fist_gesture
                        self.right_hand_open = is_open_palm
                        self.right_hand_positions.append(paddle_y_normalized)
                        
                        if self.right_hand_smoothed_y is None:
                            self.right_hand_smoothed_y = paddle_y_normalized
                        else:
                            self.right_hand_smoothed_y = (HAND_POSITION_SMOOTHING_FACTOR * paddle_y_normalized + 
                                                          (1 - HAND_POSITION_SMOOTHING_FACTOR) * self.right_hand_smoothed_y)
                        right_paddle_y = self.right_hand_smoothed_y
                    
                    if self.frame_count % HAND_LANDMARK_DRAW_FREQ == 0:
                        if is_fist_gesture:
                            l_color, c_color = COLOR_FIST, COLOR_FIST_LIGHT
                        elif hand_x >= screen_center:
                            l_color, c_color = COLOR_HAND_RIGHT, COLOR_HAND_RIGHT_LIGHT
                        else:
                            l_color, c_color = COLOR_HAND_LEFT, COLOR_HAND_LEFT_LIGHT
                        
                        self._draw_landmarks(frame, landmarks, l_color, c_color, w, h)
                
                current_both_fists = (self.left_hand_fist and self.right_hand_fist and 
                                     self.left_hand_detected and self.right_hand_detected)
                
                current_both_hands_open = (self.left_hand_open and self.right_hand_open and
                                          self.left_hand_detected and self.right_hand_detected)
                
                both_fists_just_detected = current_both_fists and not self.both_fists_detected
                both_hands_just_opened = current_both_hands_open and not self.both_hands_open
                
                self.both_fists_detected = current_both_fists
                self.both_hands_open = current_both_hands_open
            else:
                self.both_fists_detected = False
                self.both_hands_open = False
                both_fists_just_detected = False
                both_hands_just_opened = False
        else:
            left_paddle_y = None
            right_paddle_y = None
            both_fists_just_detected = False
            both_hands_just_opened = False
        
        h, w, _ = frame.shape
        
        if self.left_hand_fist and self.left_hand_detected:
            cv2.putText(frame, "LEFT FIST", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_FIST, 2)
        
        if self.right_hand_fist and self.right_hand_detected:
            cv2.putText(frame, "RIGHT FIST", (w - 150, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_FIST, 2)
        
        if self.both_hands_open:
            cv2.putText(frame, "BOTH HANDS OPEN", (w // 2 - 100, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_HAND_RIGHT, 2)
        
        if self.thumbs_up_detected:
            cv2.putText(frame, "THUMBS UP - SPEED UP!", (w // 2 - 140, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        if self.thumbs_down_detected:
            cv2.putText(frame, "THUMBS DOWN - SLOW DOWN!", (w // 2 - 170, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
        
        hand_data = {
            'left_detected': self.left_hand_detected,
            'right_detected': self.right_hand_detected,
            'left_fist': self.left_hand_fist,
            'right_fist': self.right_hand_fist,
            'both_fists': self.both_fists_detected,
            'both_fists_just_detected': both_fists_just_detected,
            'both_hands_open': self.both_hands_open,
            'both_hands_just_opened': both_hands_just_opened,
            'thumbs_up': self.thumbs_up_detected,
            'thumbs_down': self.thumbs_down_detected,
            'left_paddle_y': left_paddle_y,
            'right_paddle_y': right_paddle_y
        }
        
        return frame, hand_data
    
    def clear_buffers(self):
        """Clear hand position buffers"""
        self.left_hand_positions.clear()
        self.right_hand_positions.clear()
        self.left_hand_smoothed_y = None
        self.right_hand_smoothed_y = None
    
    def close(self):
        """Clean up resources"""
        if self.detector:
            self.detector.close()
