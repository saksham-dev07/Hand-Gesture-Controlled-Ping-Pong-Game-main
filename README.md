# 🏓 Hand Gesture Controlled Ping Pong Game

A fun and interactive ping pong game controlled entirely by hand gestures using your webcam! Move your hands to control the paddles and make a fist to serve the ball. Built with Python, OpenCV, MediaPipe, and Tkinter.

![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)
![OpenCV](https://img.shields.io/badge/opencv-4.8.1-green)
![MediaPipe](https://img.shields.io/badge/mediapipe-0.10.14-orange)

## ✨ Features

- **👐 Hand Gesture Control**: Control both paddles using your hands
- **✊ Fist Gesture to Serve**: Make a fist with either hand to start the ball
- **🎯 Real-time Hand Tracking**: Powered by Google's MediaPipe for accurate hand detection
- **🎮 Two-Player Support**: Each hand controls a different paddle
- **⏸️ Pause/Resume**: Pause the game anytime with on-screen controls
- **📊 Score Tracking**: Keep track of points for both players
- **🖥️ Fullscreen Mode**: Press F11 for immersive gameplay
- **🐛 Debug Mode**: Press 'D' to toggle debug visualization
- **⚡ GPU Acceleration**: Automatically uses CUDA if available for better performance
- **🎨 Modern UI**: Clean and intuitive Tkinter interface

## 🎮 How to Play

1. **Starting the Game**: 
   - Position yourself in front of your webcam
   - Click the "Start" button or it will auto-start when hands are detected
   
2. **Controlling Paddles**:
   - **Left Hand**: Controls the left paddle (moves up and down with your hand)
   - **Right Hand**: Controls the right paddle (moves up and down with your hand)
   
3. **Serving the Ball**:
   - Make a **fist** with either hand (close all fingers)
   - The ball will launch from the serving player's side
   
4. **Scoring**:
   - Score points when your opponent misses the ball
   - First to reach the target score wins!

5. **Controls**:
   - **Pause Button**: Pause/resume the game
   - **F11**: Toggle fullscreen mode
   - **ESC**: Exit fullscreen mode
   - **D**: Toggle debug mode (shows hand landmarks)
   - **Quit Button**: Exit the game

## 🚀 Quick Start

### Prerequisites

- Windows OS (batch files provided)
- Python 3.11 or 3.12
- Webcam

### Easy Installation (Recommended)

1. **Clone or download this repository**

2. **Run the automatic installer**:
   ```batch
   INSTALL.bat
   ```
   This will:
   - Detect compatible Python version
   - Create a virtual environment
   - Install all dependencies automatically

3. **Start playing**:
   ```batch
   play_refactored.bat
   ```

### Manual Installation

If you prefer to install manually:

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   ```bash
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the game**:
   ```bash
   python hand_refactored.py
   ```

## 📦 Dependencies

- **opencv-python** (4.8.1.78) - Computer vision and camera handling
- **mediapipe** (0.10.14) - Hand detection and tracking
- **pillow** (10.0.1) - Image processing
- **numpy** (≥1.26.0) - Numerical operations

## 🏗️ Project Structure

```
Hand-Gesture-Controlled-Ping-Pong-Game/
├── hand_refactored.py      # Main application entry point
├── config.py                # Game configuration and constants
├── hand_detector.py         # Hand detection and gesture recognition
├── game_objects.py          # Ball and Paddle classes
├── game_engine.py           # Game logic and physics
├── ui_manager.py            # User interface management
├── requirements.txt         # Python dependencies
├── setup.py                 # Automatic setup script
├── INSTALL.bat             # Windows installer
├── play_refactored.bat     # Game launcher
└── README.md               # This file
```

## ⚙️ Configuration

You can customize the game by modifying values in `config.py`:

### Game Settings
- `CANVAS_WIDTH`, `CANVAS_HEIGHT` - Game canvas dimensions
- `FRAME_SKIP` - Process hands every N frames for performance

### Camera Settings
- `CAMERA_WIDTH`, `CAMERA_HEIGHT` - Camera resolution
- `CAMERA_FPS` - Camera frame rate

### Hand Detection
- `MIN_DETECTION_CONFIDENCE` - Hand detection confidence threshold
- `MIN_TRACKING_CONFIDENCE` - Hand tracking confidence threshold
- `MAX_NUM_HANDS` - Maximum number of hands to detect

### Paddle Settings
- `PADDLE_WIDTH`, `PADDLE_HEIGHT` - Paddle dimensions
- `PADDLE_SPEED` - Paddle movement speed
- `PADDLE_SMOOTHING` - Paddle movement smoothing factor

### Ball Settings
- `BALL_RADIUS` - Ball size
- `BALL_INITIAL_SPEED` - Starting ball speed
- `BALL_SPEED_INCREMENT` - Speed increase per hit
- `MAX_BALL_SPEED` - Maximum ball speed

## 🎯 Tips for Best Experience

1. **Lighting**: Ensure good lighting conditions for better hand detection
2. **Distance**: Position yourself 2-3 feet from the webcam
3. **Background**: Use a plain background for better hand tracking
4. **Calibration**: The game calibrates paddle positions automatically
5. **Smooth Movements**: Move your hands smoothly for better control

## 🐛 Troubleshooting

### Camera Not Opening
- Check if another application is using the webcam
- Try changing `CAMERA_INDEX` in `config.py` (default is 0)

### Hand Detection Issues
- Ensure good lighting
- Keep your hands within the camera frame
- Try adjusting `MIN_DETECTION_CONFIDENCE` in `config.py`

### Performance Issues
- Lower the `CAMERA_WIDTH` and `CAMERA_HEIGHT` in `config.py`
- Increase `FRAME_SKIP` for less frequent hand processing
- Close other resource-intensive applications

### Installation Issues
- Make sure you have Python 3.11 or 3.12 installed
- Try running as administrator
- Manually install dependencies: `pip install -r requirements.txt`

## 🔧 Advanced Features

### Debug Mode
Press 'D' during gameplay to toggle debug mode, which displays:
- Hand landmarks and connections
- Hand confidence scores
- Fist detection status
- FPS counter

### GPU Acceleration
The game automatically detects and uses CUDA-capable GPUs for better performance. Check the startup messages to see if GPU acceleration is enabled.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📝 License

This project is open source and available for educational and personal use.

## 🎓 Technologies Used

- **Python** - Core programming language
- **OpenCV** - Computer vision and camera handling
- **MediaPipe** - Google's ML framework for hand tracking
- **Tkinter** - GUI framework
- **NumPy** - Numerical computations
- **Pillow** - Image processing

## 🌟 Acknowledgments

- Google MediaPipe team for the excellent hand tracking solution
- OpenCV community for computer vision tools

## 📧 Support

If you encounter any issues or have questions:
1. Check the Troubleshooting section
2. Review the configuration options in `config.py`
3. Enable debug mode (press 'D') to diagnose issues

---

**Enjoy playing! 🏓**

Made with ❤️ using Python and Computer Vision
