# Contributing to Hand Gesture Controlled Ping Pong Game

Thank you for your interest in contributing! We welcome contributions from developers of all skill levels.

## How to Contribute

1. **Fork the Repository**: Click the "Fork" button at the top right of the project page.
2. **Clone Your Fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Hand-Gesture-Controlled-Ping-Pong-Game.git
   cd Hand-Gesture-Controlled-Ping-Pong-Game
   ```
3. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make Your Changes**: Ensure your code follows the existing style and clean multi-threaded architecture.
5. **Run Setup & Test**:
   ```bash
   python setup.py
   python src/main.py
   ```
6. **Commit & Push**:
   ```bash
   git commit -m "Add descriptive summary of changes"
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request**: Submit a PR to the `main` branch with a details of your changes.

## Code Guidelines

- Follow PEP 8 guidelines for Python code formatting.
- Maintain thread safety when interacting with `CameraThread` and GUI components.
- Keep configuration parameters centralized in `src/config.py`.

## Reporting Issues

If you find a bug or have a feature request, please submit an issue on the repository Issue Tracker with steps to reproduce and system details (OS, Python version, webcam setup).
