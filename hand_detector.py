"""
Hand Detection Module
Handles MediaPipe hand detection, tracking, and gesture recognition (fist detection)
OPTIMIZED: CPU-only version with all GPU code removed
"""

import cv2
import mediapipe as mp
import numpy as np
from collections import deque
from config import *


class HandDetector:
    """Handles hand detection and gesture recognition using MediaPipe"""
    
    def __init__(self):
        """Initialize the hand detector"""
        print("💻 Using optimized CPU mode for hand detection")
        
        # Initialize MediaPipe with optimized settings
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_NUM_HANDS,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
            model_complexity=MODEL_COMPLEXITY
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Hand tracking state
        self.left_hand_detected = False
        self.right_hand_detected = False
        self.left_hand_fist = False
        self.right_hand_fist = False
        self.both_fists_detected = False
        self.both_hands_open = False  # Track when both hands are open
        
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
            print("="*60)
            print("You will now see detailed fist detection data in console:")
            print("• Finger extension ratios")
            print("• Which fingers are detected as closed")
            print("• Final fist detection result")
            print("="*60 + "\n")
        else:
            print("\n" + "="*60)
            print("🔍 DEBUG MODE DISABLED")
            print("="*60 + "\n")
    
    @staticmethod
    def _distance(p1, p2):
        """Calculate 3D distance between two landmarks"""
        return ((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)**0.5
    
    def is_fist(self, landmarks, debug=False):
        """
        Improved fist detection using finger extension ratios
        Returns True if hand is making a fist, False otherwise
        
        STRICT MODE: Requires very tight fist to avoid false detection when bending palm
        """
        # Key landmarks
        wrist = landmarks.landmark[0]
        
        # Finger tips: index=8, middle=12, ring=16, pinky=20
        # Finger PIPs (middle joints): index=6, middle=10, ring=14, pinky=18
        # Finger MCPs (knuckles): index=5, middle=9, ring=13, pinky=17
        # Thumb: tip=4, mcp=2
        
        # Calculate finger extension ratios
        fingers_data = {
            'index': {'tip': 8, 'pip': 6, 'mcp': 5},
            'middle': {'tip': 12, 'pip': 10, 'mcp': 9},
            'ring': {'tip': 16, 'pip': 14, 'mcp': 13},
            'pinky': {'tip': 20, 'pip': 18, 'mcp': 17}
        }
        
        finger_ratios = {}
        fingers_closed = 0
        
        for finger_name, indices in fingers_data.items():
            tip = landmarks.landmark[indices['tip']]
            mcp = landmarks.landmark[indices['mcp']]
            
            tip_dist = self._distance(tip, wrist)
            mcp_dist = self._distance(mcp, wrist)
            
            # Avoid division by zero
            if mcp_dist > 0:
                ratio = tip_dist / mcp_dist
                finger_ratios[finger_name] = ratio
                
                # STRICTER fist detection: tip should be VERY close to knuckle
                if ratio < FINGER_CLOSED_RATIO:
                    fingers_closed += 1
                    
                if debug:
                    print(f"  {finger_name}: ratio={ratio:.3f} {'✊ CLOSED' if ratio < FINGER_CLOSED_RATIO else '✋ OPEN'}")
        
        # Check thumb position - should be tucked in for a real fist
        thumb_tip = landmarks.landmark[4]
        thumb_mcp = landmarks.landmark[2]
        thumb_ratio = self._distance(thumb_tip, wrist) / self._distance(thumb_mcp, wrist)
        
        # For a real fist, thumb should be curled too
        thumb_closed = thumb_ratio < THUMB_CLOSED_RATIO
        
        if debug:
            print(f"  thumb: ratio={thumb_ratio:.3f} {'✊ CLOSED' if thumb_closed else '✋ OPEN'}")
        
        # STRICT fist detection: ALL 4 fingers must be tightly closed AND thumb curled
        is_fist = fingers_closed == 4 and thumb_closed
        
        if debug:
            print(f"Fingers closed: {fingers_closed}/4, Thumb closed: {thumb_closed} → {'✊ FIST DETECTED' if is_fist else '✋ OPEN HAND'}")
            print(f"Ratios: {finger_ratios}")
            print("-" * 50)
        
        return is_fist
    
    def is_thumbs_up(self, landmarks):
        """
        Detect thumbs up gesture
        Returns True if thumb is extended upward and other fingers are closed
        """
        wrist = landmarks.landmark[0]
        thumb_tip = landmarks.landmark[4]
        thumb_ip = landmarks.landmark[3]
        thumb_mcp = landmarks.landmark[2]
        
        index_tip = landmarks.landmark[8]
        middle_tip = landmarks.landmark[12]
        ring_tip = landmarks.landmark[16]
        pinky_tip = landmarks.landmark[20]
        
        index_pip = landmarks.landmark[6]
        middle_pip = landmarks.landmark[10]
        ring_pip = landmarks.landmark[14]
        pinky_pip = landmarks.landmark[18]
        
        # Thumb should be extended upward (tip higher than base in y-coordinate)
        thumb_extended_up = thumb_tip.y < thumb_mcp.y - 0.1
        
        # Thumb should be reasonably far from wrist
        thumb_dist = self._distance(thumb_tip, wrist)
        thumb_extended = thumb_dist > 0.2
        
        # Other fingers should be curled (tips close to or below PIPs)
        fingers_curled = (
            index_tip.y >= index_pip.y - 0.05 and
            middle_tip.y >= middle_pip.y - 0.05 and
            ring_tip.y >= ring_pip.y - 0.05 and
            pinky_tip.y >= pinky_pip.y - 0.05
        )
        
        return thumb_extended_up and thumb_extended and fingers_curled
    
    def is_thumbs_down(self, landmarks):
        """
        Detect thumbs down gesture
        Returns True if thumb is extended downward and other fingers are closed
        """
        wrist = landmarks.landmark[0]
        thumb_tip = landmarks.landmark[4]
        thumb_ip = landmarks.landmark[3]
        thumb_mcp = landmarks.landmark[2]
        
        index_tip = landmarks.landmark[8]
        middle_tip = landmarks.landmark[12]
        ring_tip = landmarks.landmark[16]
        pinky_tip = landmarks.landmark[20]
        
        index_pip = landmarks.landmark[6]
        middle_pip = landmarks.landmark[10]
        ring_pip = landmarks.landmark[14]
        pinky_pip = landmarks.landmark[18]
        
        # Thumb should be extended downward (tip lower than base in y-coordinate)
        thumb_extended_down = thumb_tip.y > thumb_mcp.y + 0.1
        
        # Thumb should be reasonably far from wrist
        thumb_dist = self._distance(thumb_tip, wrist)
        thumb_extended = thumb_dist > 0.2
        
        # Other fingers should be curled (tips close to or below PIPs)
        fingers_curled = (
            index_tip.y >= index_pip.y - 0.05 and
            middle_tip.y >= middle_pip.y - 0.05 and
            ring_tip.y >= ring_pip.y - 0.05 and
            pinky_tip.y >= pinky_pip.y - 0.05
        )
        
        return thumb_extended_down and thumb_extended and fingers_curled
    
    def process_frame(self, frame):
        """
        Process a camera frame and detect hands
        Returns: (processed_frame, hand_data)
        """
        self.frame_count += 1
        
        # Flip for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Only process hands every N frames for better performance
        if self.frame_count % FRAME_SKIP == 0:
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process hands (MediaPipe uses optimized CPU processing)
            results = self.hands.process(rgb_frame)
            
            # Reset hand detection
            self.left_hand_detected = False
            self.right_hand_detected = False
            self.left_hand_fist = False
            self.right_hand_fist = False
            self.thumbs_up_detected = False
            self.thumbs_down_detected = False
            
            left_paddle_y = None
            right_paddle_y = None
            
            if results.multi_hand_landmarks and results.multi_handedness:
                h, w, _ = frame.shape
                screen_center = w / 2
                
                for landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    # Determine if it's left or right hand
                    hand_label = handedness.classification[0].label
                    confidence = handedness.classification[0].score
                    
                    # Only process if confidence is high enough
                    if confidence < HAND_CONFIDENCE_THRESHOLD:
                        continue
                    
                    # Detect gestures
                    is_fist_gesture = self.is_fist(landmarks, debug=self.debug_fist_detection)
                    is_thumbs_up_gesture = self.is_thumbs_up(landmarks)
                    is_thumbs_down_gesture = self.is_thumbs_down(landmarks)
                    
                    # Track thumbs up/down (only need one hand for speed control)
                    if is_thumbs_up_gesture:
                        self.thumbs_up_detected = True
                    if is_thumbs_down_gesture:
                        self.thumbs_down_detected = True
                    
                    # Debug output for fist detection
                    if self.debug_fist_detection:
                        print(f"\n{'='*50}")
                        print(f"🖐️ Analyzing {hand_label} hand (confidence: {confidence:.2f})")
                    
                    # Get hand position (using middle finger tip - landmark 12)
                    middle_finger = landmarks.landmark[12]
                    
                    # Convert to pixel coordinates
                    hand_x = middle_finger.x * w
                    hand_y = middle_finger.y * h
                    
                    # Map to paddle position (normalized 0-1)
                    paddle_y_normalized = hand_y / h
                    
                    # Determine which side of screen the hand is on
                    if hand_x < screen_center:  # Hand on LEFT side of screen
                        self.left_hand_detected = True
                        self.left_hand_fist = is_fist_gesture
                        self.left_hand_positions.append(paddle_y_normalized)
                        
                        # Apply exponential smoothing for stable movement
                        if self.left_hand_smoothed_y is None:
                            self.left_hand_smoothed_y = paddle_y_normalized
                        else:
                            self.left_hand_smoothed_y = (HAND_POSITION_SMOOTHING_FACTOR * paddle_y_normalized + 
                                                         (1 - HAND_POSITION_SMOOTHING_FACTOR) * self.left_hand_smoothed_y)
                        left_paddle_y = self.left_hand_smoothed_y
                    else:  # Hand on RIGHT side of screen
                        self.right_hand_detected = True
                        self.right_hand_fist = is_fist_gesture
                        self.right_hand_positions.append(paddle_y_normalized)
                        
                        # Apply exponential smoothing for stable movement
                        if self.right_hand_smoothed_y is None:
                            self.right_hand_smoothed_y = paddle_y_normalized
                        else:
                            self.right_hand_smoothed_y = (HAND_POSITION_SMOOTHING_FACTOR * paddle_y_normalized + 
                                                          (1 - HAND_POSITION_SMOOTHING_FACTOR) * self.right_hand_smoothed_y)
                        right_paddle_y = self.right_hand_smoothed_y
                    
                    # Draw hand landmarks on frame (every N frames for performance)
                    if self.frame_count % HAND_LANDMARK_DRAW_FREQ == 0:
                        # Different colors for left and right hands
                        # Change color to red/orange if making fist
                        if is_fist_gesture:
                            landmark_color = COLOR_FIST
                            connection_color = COLOR_FIST_LIGHT
                        elif hand_label == "Right":
                            landmark_color = COLOR_HAND_RIGHT
                            connection_color = COLOR_HAND_RIGHT_LIGHT
                        else:
                            landmark_color = COLOR_HAND_LEFT
                            connection_color = COLOR_HAND_LEFT_LIGHT
                        
                        self.mp_draw.draw_landmarks(
                            frame, 
                            landmarks, 
                            self.mp_hands.HAND_CONNECTIONS,
                            self.mp_draw.DrawingSpec(color=landmark_color, thickness=2, circle_radius=3),
                            self.mp_draw.DrawingSpec(color=connection_color, thickness=2)
                        )
                
                # Update both fists detected state
                current_both_fists = (self.left_hand_fist and self.right_hand_fist and 
                                     self.left_hand_detected and self.right_hand_detected)
                
                # Update both hands open state (both detected but neither making fist)
                current_both_hands_open = (not self.left_hand_fist and not self.right_hand_fist and
                                          self.left_hand_detected and self.right_hand_detected)
                
                # Detect transitions (for pause/resume)
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
            # Not processing hands this frame, maintain previous state
            left_paddle_y = None
            right_paddle_y = None
            both_fists_just_detected = False
            both_hands_just_opened = False
        
        # Add visual feedback for gestures on the frame
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
        
        # Visual feedback for thumbs up/down
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
        if self.hands:
            self.hands.close()