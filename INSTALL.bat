@echo off
chcp 65001 >nul
title 🏓 Hand Gesture Controlled Ping Pong Game

echo.
echo ============================================================
echo 🏓 Hand Gesture Controlled Ping Pong Game
echo ============================================================
echo.

REM Check Python availability if venv doesn't exist
if not exist venv\Scripts\python.exe (
    where python >nul 2>nul
    if errorlevel 1 (
        echo ❌ Python was not found in your PATH!
        echo 💡 Please install Python 3.11 or 3.12 from python.org and add it to PATH.
        echo.
        pause
        exit /b 1
    )
    echo 🔧 Virtual environment not found. Running setup...
    python setup.py
    echo.
) else (
    echo ✅ Virtual environment ready.
)

REM Verify venv after setup attempt
if not exist venv\Scripts\python.exe (
    echo ❌ Virtual environment initialization failed!
    echo Please check the error messages above.
    echo.
    pause
    exit /b 1
)

echo 🚀 Launching Hand Pong Game...
echo.

REM Run application via venv Python
venv\Scripts\python.exe src\main.py

if errorlevel 1 (
    echo.
    echo ❌ Game exited with an error.
    echo.
    pause
) else (
    echo.
    echo ✅ Game closed successfully!
    timeout /t 2 >nul
)