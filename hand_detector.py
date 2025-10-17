"""
Hand Detection Module
Handles MediaPipe hand detection, tracking, and gesture recognition (fist detection)
"""

import cv2
import mediapipe as mp
import numpy as np
from collections import deque
from config import *


class HandDetector:
    """Handles hand detection and gesture recognition using MediaPipe"""
    
    def __init__(self, use_gpu=False):
        """Initialize the hand detector"""
        self.use_gpu = use_gpu
        
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
        
        # Hand position smoothing
        self.left_hand_positions = deque(maxlen=HAND_POSITION_BUFFER_SIZE)
        self.right_hand_positions = deque(maxlen=HAND_POSITION_BUFFER_SIZE)
        
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
    def check_gpu_support():
        """Check if GPU/CUDA is available for OpenCV"""
        try:
            if cv2.cuda.getCudaEnabledDeviceCount() > 0:
                print(f"🎮 GPU DETECTED! Found {cv2.cuda.getCudaEnabledDeviceCount()} CUDA device(s)")
                print(f"   Device: {cv2.cuda.printCudaDeviceInfo(0)}")
                return True
            else:
                print("💻 No GPU detected, using CPU (this is fine!)")
                return False
        except:
            print("💻 GPU acceleration not available, using CPU")
            return False
    
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
            
            # Process hands
            results = self.hands.process(rgb_frame)
            
            # Reset hand detection
            self.left_hand_detected = False
            self.right_hand_detected = False
            self.left_hand_fist = False
            self.right_hand_fist = False
            
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
                    
                    # Detect fist gesture with optional debug output
                    if self.debug_fist_detection:
                        print(f"\n{'='*50}")
                        print(f"🖐️ Analyzing {hand_label} hand (confidence: {confidence:.2f})")
                    
                    is_fist_gesture = self.is_fist(landmarks, debug=self.debug_fist_detection)
                    
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
                        # Smooth movement
                        left_paddle_y = sum(self.left_hand_positions) / len(self.left_hand_positions)
                    else:  # Hand on RIGHT side of screen
                        self.right_hand_detected = True
                        self.right_hand_fist = is_fist_gesture
                        self.right_hand_positions.append(paddle_y_normalized)
                        # Smooth movement
                        right_paddle_y = sum(self.right_hand_positions) / len(self.right_hand_positions)
                    
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
                
                # Detect transition (for pause/resume)
                both_fists_just_detected = current_both_fists and not self.both_fists_detected
                self.both_fists_detected = current_both_fists
            else:
                self.both_fists_detected = False
                both_fists_just_detected = False
        else:
            # Not processing hands this frame, maintain previous state
            left_paddle_y = None
            right_paddle_y = None
            both_fists_just_detected = False
        
        # Add visual feedback for fist gesture on the frame
        h, w, _ = frame.shape
        
        if self.left_hand_fist and self.left_hand_detected:
            cv2.putText(frame, "LEFT FIST", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_FIST, 2)
        
        if self.right_hand_fist and self.right_hand_detected:
            cv2.putText(frame, "RIGHT FIST", (w - 150, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_FIST, 2)
        
        hand_data = {
            'left_detected': self.left_hand_detected,
            'right_detected': self.right_hand_detected,
            'left_fist': self.left_hand_fist,
            'right_fist': self.right_hand_fist,
            'both_fists': self.both_fists_detected,
            'both_fists_just_detected': both_fists_just_detected,
            'left_paddle_y': left_paddle_y,
            'right_paddle_y': right_paddle_y
        }
        
        return frame, hand_data
    
    def clear_buffers(self):
        """Clear hand position buffers"""
        self.left_hand_positions.clear()
        self.right_hand_positions.clear()
    
    def close(self):
        """Clean up resources"""
        if self.hands:
            self.hands.close()
