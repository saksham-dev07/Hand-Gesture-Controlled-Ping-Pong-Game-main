"""
Configuration file for Hand Gesture Pong Game
Contains all constants, settings, and configuration values
"""

# ============================================================================
# GAME SETTINGS
# ============================================================================

# Canvas dimensions
CANVAS_WIDTH = 720
CANVAS_HEIGHT = 480

# Frame processing
FRAME_SKIP = 1  # No skipping needed with background thread

# Game Modes & States
MODE_1PLAYER = '1P_VS_AI'
MODE_2PLAYER = '2P_LOCAL'

STATE_MENU = 'MENU'
STATE_CALIBRATING = 'CALIBRATING'
STATE_PLAYING = 'PLAYING'

CALIBRATION_COUNTDOWN_SECONDS = 3

# ============================================================================
# CAMERA SETTINGS
# ============================================================================

# Camera resolution
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 60
CAMERA_BUFFER_SIZE = 1

# ============================================================================
# MEDIAPIPE SETTINGS
# ============================================================================

# Hand detection settings
MAX_NUM_HANDS = 2
MIN_DETECTION_CONFIDENCE = 0.6
MIN_TRACKING_CONFIDENCE = 0.6
# MODEL_COMPLEXITY is no longer used in the modern MediaPipe Tasks API

# Hand confidence threshold
HAND_CONFIDENCE_THRESHOLD = 0.5

# Hand position smoothing
HAND_POSITION_BUFFER_SIZE = 8  # Increased for better stability
HAND_POSITION_SMOOTHING_FACTOR = 0.3  # Exponential smoothing (0-1, lower = smoother)
HAND_POSITION_DEADZONE = 0.0  # Disabled deadzone, relying on EMA for smooth movement

# ============================================================================
# FIST DETECTION SETTINGS
# ============================================================================

# Fist detection thresholds (strict mode to avoid false positives)
FINGER_CLOSED_RATIO = 1.0  # Finger tip to knuckle ratio threshold
THUMB_CLOSED_RATIO = 1.3   # Thumb curl threshold

# ============================================================================
# GAME OBJECTS
# ============================================================================

# Ball settings
BALL_RADIUS = 8
BALL_INITIAL_SPEED = 5
BALL_MAX_SPEED = 18  # Increased max speed for thumbs up
BALL_MIN_SPEED = 3   # Minimum speed for thumbs down
BALL_SPEED_INCREASE = 1.05  # Speed multiplier on paddle hit
BALL_SPEED_CHANGE_AMOUNT = 1.5  # Speed change per thumbs up/down gesture

# Paddle settings
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 80
PADDLE_SPEED = 6
PADDLE1_X = 20  # Left paddle
PADDLE2_X = 690  # Right paddle (CANVAS_WIDTH - PADDLE_WIDTH - 20)

# ============================================================================
# AI SETTINGS
# ============================================================================

AI_DIFFICULTY = 0.7  # 0.0 to 1.0 (reaction accuracy)
AI_ERROR_MARGIN = 20  # Pixels of error in AI targeting
AI_SPEED = 4  # AI paddle movement speed

# ============================================================================
# UI/WINDOW SETTINGS
# ============================================================================

# Main window
WINDOW_WIDTH = 1150
WINDOW_HEIGHT = 650
WINDOW_TITLE = "🎮 Hand Gesture Pong - AI Edition"

# Camera preview dimensions
CAMERA_PREVIEW_WIDTH = 352
CAMERA_PREVIEW_HEIGHT = 264

# ============================================================================
# COLORS (Modern Dark Theme)
# ============================================================================

# Background colors
BG_PRIMARY = '#0a0e27'
BG_SECONDARY = '#1a1f3a'
BG_TERTIARY = '#1e293b'
BG_DARK = '#0f172a'
BG_CANVAS = '#0a0e1f'

# Text colors
TEXT_PRIMARY = '#60a5fa'
TEXT_SECONDARY = '#94a3b8'
TEXT_LIGHT = '#cbd5e1'
TEXT_DARK = '#64748b'

# Accent colors
COLOR_SUCCESS = '#10b981'
COLOR_SUCCESS_LIGHT = '#34d399'
COLOR_SUCCESS_DARK = '#059669'
COLOR_WARNING = '#fbbf24'
COLOR_WARNING_DARK = '#d97706'
COLOR_DANGER = '#ef4444'
COLOR_DANGER_DARK = '#dc2626'
COLOR_DANGER_DARKER = '#991b1b'
COLOR_INFO = '#60a5fa'
COLOR_INFO_DARK = '#3b82f6'

# Game object colors
COLOR_PADDLE_ACTIVE = '#00ff00'  # Bright green when hand-controlled
COLOR_PADDLE_INACTIVE = '#475569'  # Gray when AI-controlled
COLOR_PADDLE_OUTLINE_ACTIVE = '#00ff00'  # Bright green outline
COLOR_PADDLE_OUTLINE_INACTIVE = '#64748b'  # Gray outline
COLOR_BALL_ACTIVE = '#60a5fa'
COLOR_BALL_INACTIVE = '#e5e7eb'
COLOR_BALL_OUTLINE_ACTIVE = '#3b82f6'
COLOR_BALL_OUTLINE_INACTIVE = '#cbd5e1'
COLOR_BALL_TRAIL = '#3b82f6'
COLOR_BALL_TRAIL_INACTIVE = '#94a3b8'
COLOR_CENTER_LINE = '#1e293b'

# Fist detection colors (for camera overlay)
COLOR_FIST = (220, 38, 38)  # Red (BGR for OpenCV)
COLOR_FIST_LIGHT = (239, 68, 68)
COLOR_HAND_RIGHT = (34, 197, 94)  # Green
COLOR_HAND_RIGHT_LIGHT = (16, 185, 129)
COLOR_HAND_LEFT = (59, 130, 246)  # Blue
COLOR_HAND_LEFT_LIGHT = (37, 99, 235)

# ============================================================================
# FONTS
# ============================================================================

FONT_FAMILY = 'Segoe UI'
FONT_TITLE = (FONT_FAMILY, 28, 'bold')
FONT_SUBTITLE = (FONT_FAMILY, 11)
FONT_HEADER = (FONT_FAMILY, 12, 'bold')
FONT_NORMAL = (FONT_FAMILY, 10)
FONT_NORMAL_BOLD = (FONT_FAMILY, 10, 'bold')
FONT_BUTTON_LARGE = (FONT_FAMILY, 16, 'bold')
FONT_BUTTON_MEDIUM = (FONT_FAMILY, 12, 'bold')
FONT_BUTTON_SMALL = (FONT_FAMILY, 11, 'bold')
FONT_BADGE = (FONT_FAMILY, 9, 'bold')
FONT_BADGE_SMALL = (FONT_FAMILY, 9)
FONT_SCORE = (FONT_FAMILY, 14, 'bold')
FONT_PAUSE_LARGE = (FONT_FAMILY, 42, 'bold')
FONT_PAUSE_SMALL = (FONT_FAMILY, 14)

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================

# FPS tracking
FPS_BUFFER_SIZE = 30
TARGET_FRAME_TIME = 16  # milliseconds (60 FPS)

# Update frequencies
CAMERA_PREVIEW_UPDATE_FREQ = 1  # Update every frame
FPS_DISPLAY_UPDATE_FREQ = 5     # Update every N frames
HAND_LANDMARK_DRAW_FREQ = 1     # Draw every frame (no skipping needed on background thread)

# ============================================================================
# MESSAGES
# ============================================================================

WELCOME_MESSAGE = """🎮 HAND PONG GAME

✨ This is a Python Desktop Application
(Not a web browser game)

📋 HOW TO PLAY:
1️⃣ Click 'START GAME' button
2️⃣ Allow camera access
3️⃣ Show your hands to the camera
4️⃣ Move hands UP/DOWN to control paddles

✊ GESTURE CONTROLS:
• Make FISTS with BOTH hands = PAUSE game
• Open BOTH hands (show palms) = RESUME game
• Hands turn RED when fist detected!
• Hands turn BLUE/GREEN when open!

⚡ BALL SPEED CONTROLS:
• 👍 THUMBS UP = Increase ball speed
• 👎 THUMBS DOWN = Decrease ball speed

⌨️ KEYBOARD SHORTCUTS:
• F11: Toggle Fullscreen
• ESC: Exit Fullscreen
• D: Toggle Debug Mode (shows fist data)

🎯 CONTROL MODES:
• 1 Hand: You vs AI
• 2 Hands: Full manual control

Ready to play? 🎮"""

CAMERA_ERROR_MESSAGE = """Cannot access camera!

Troubleshooting:
• Make sure camera is connected
• Close other apps using camera
• Check camera permissions
• Try restarting the application"""

DEPENDENCIES_MESSAGE = """Make sure you have installed all dependencies:
   pip install opencv-python mediapipe pillow numpy"""
