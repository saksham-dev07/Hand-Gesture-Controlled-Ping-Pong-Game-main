@echo off
echo 🔧 Running Automatic Setup...
echo.
python setup.py

echo.
echo ========================================
echo 🎮 Setup complete! Launching game...
echo ========================================
echo.
timeout /t 2 /nobreak >nul

echo 🏓 Hand Gesture Controlled Ping Pong Game - REFACTORED VERSION
echo ==============================================================
echo.

REM Check if venv exists
if not exist venv\Scripts\python.exe (
    echo ❌ Virtual environment not found!
    echo Setup may have failed. Please check the errors above.
    pause
    exit /b 1
)

REM Run the refactored version using venv Python
venv\Scripts\python.exe src\main.py

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