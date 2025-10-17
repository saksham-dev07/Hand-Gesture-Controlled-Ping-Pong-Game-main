@echo off
echo 🏓 Hand Gesture Controlled Ping Pong Game - REFACTORED VERSION
echo ==============================================================
echo.

REM Check if virtual environment exists
if not exist venv\Scripts\python.exe (
    echo ❌ Virtual environment not found!
    echo.
    echo Please run INSTALL.bat first to set up the environment.
    echo.
    pause
    exit /b 1
)

echo ✅ Using virtual environment...
echo 🚀 Starting refactored modular version...
echo.

REM Run the refactored version using venv Python
venv\Scripts\python.exe hand_refactored.py

REM Pause to see any errors
if errorlevel 1 (
    echo.
    echo ❌ Game exited with an error!
    echo.
    pause
) else (
    echo.
    echo ✅ Game closed successfully!
    timeout /t 2 >nul
)
