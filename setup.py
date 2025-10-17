"""
Automatic Setup Script for Hand Gesture Controlled Ping Pong Game
This script will:
1. Find compatible Python version (3.11 or 3.12)
2. Create virtual environment
3. Install all dependencies
4. Configure the environment
"""
import subprocess
import sys
import os
import shutil
from pathlib import Path

def find_python_executable():
    """Find a compatible Python version (3.11 or 3.12) on the system"""
    print("🔍 Searching for compatible Python version...")
    
    # Check current Python
    current_version = sys.version_info
    print(f"   Current Python: {current_version.major}.{current_version.minor}.{current_version.micro}")
    
    if current_version.major == 3 and current_version.minor in [11, 12]:
        print(f"✅ Current Python {current_version.major}.{current_version.minor} is compatible!")
        return sys.executable
    
    # Try to find other Python versions
    possible_commands = [
        'py -3.12',
        'py -3.11', 
        'python3.12',
        'python3.11',
        'python312',
        'python311'
    ]
    
    for cmd in possible_commands:
        try:
            result = subprocess.run(
                f'{cmd} --version',
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_str = result.stdout.strip()
                print(f"✅ Found compatible Python: {version_str}")
                # Get the full path
                path_result = subprocess.run(
                    f'{cmd} -c "import sys; print(sys.executable)"',
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if path_result.returncode == 0:
                    return path_result.stdout.strip()
        except (subprocess.TimeoutExpired, Exception):
            continue
    
    print("\n⚠️ No compatible Python version found (3.11 or 3.12)")
    print("📥 Please install Python 3.12 from: https://www.python.org/downloads/")
    print("   Make sure to check 'Add Python to PATH' during installation")
    return None

def create_venv(python_exe):
    """Create virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("\n🗑️ Removing existing virtual environment...")
        try:
            shutil.rmtree(venv_path)
        except Exception as e:
            print(f"⚠️ Could not remove old venv: {e}")
            print("   Please delete the 'venv' folder manually and run setup again.")
            return False
    
    print("\n📦 Creating virtual environment with compatible Python...")
    try:
        subprocess.check_call([python_exe, '-m', 'venv', 'venv'])
        print("✅ Virtual environment created successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def get_venv_python():
    """Get the path to the venv Python executable"""
    if os.name == 'nt':  # Windows
        return os.path.join('venv', 'Scripts', 'python.exe')
    else:  # Linux/Mac
        return os.path.join('venv', 'bin', 'python')

def install_dependencies():
    """Install all required dependencies in the virtual environment"""
    print("\n📥 Installing dependencies...")
    venv_python = get_venv_python()
    
    try:
        # Upgrade pip
        print("⬆️ Upgrading pip...")
        subprocess.check_call([venv_python, '-m', 'pip', 'install', '--upgrade', 'pip'])
        
        # Install from requirements.txt
        print("📦 Installing packages from requirements.txt...")
        subprocess.check_call([venv_python, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        
        print("✅ All dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_launcher():
    """Create a launcher script that automatically uses the venv"""
    print("\n🚀 Creating launcher script...")
    
    if os.name == 'nt':  # Windows
        launcher_content = """@echo off
echo 🏓 Hand Gesture Controlled Ping Pong Game
echo ==========================================
echo.

if not exist venv\\Scripts\\python.exe (
    echo ❌ Virtual environment not found!
    echo Please run setup.py first.
    pause
    exit /b 1
)

echo ✅ Using virtual environment...
venv\\Scripts\\python.exe hand.py
pause
"""
        launcher_path = "play.bat"
    else:  # Linux/Mac
        launcher_content = """#!/bin/bash
echo "🏓 Hand Gesture Controlled Ping Pong Game"
echo "=========================================="
echo ""

if [ ! -f venv/bin/python ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run setup.py first."
    exit 1
fi

echo "✅ Using virtual environment..."
venv/bin/python hand.py
"""
        launcher_path = "play.sh"
    
    try:
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        
        if os.name != 'nt':  # Make executable on Linux/Mac
            os.chmod(launcher_path, 0o755)
        
        print(f"✅ Created launcher: {launcher_path}")
        return True
    except Exception as e:
        print(f"⚠️ Could not create launcher: {e}")
        return False

def verify_installation():
    """Verify that all packages are properly installed"""
    print("\n🔍 Verifying installation...")
    venv_python = get_venv_python()
    
    test_code = """
import sys
try:
    import cv2
    import mediapipe
    import PIL
    import numpy
    print("✅ All packages imported successfully!")
    print(f"   - OpenCV: {cv2.__version__}")
    print(f"   - MediaPipe: {mediapipe.__version__}")
    print(f"   - NumPy: {numpy.__version__}")
    sys.exit(0)
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
"""
    
    try:
        result = subprocess.run(
            [venv_python, '-c', test_code],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return result.returncode == 0
    except Exception as e:
        print(f"⚠️ Verification failed: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("🏓 Hand Gesture Controlled Ping Pong Game - Automatic Setup")
    print("=" * 60)
    
    # Find compatible Python
    python_exe = find_python_executable()
    if not python_exe:
        input("\nPress Enter to exit...")
        return
    
    # Create virtual environment
    if not create_venv(python_exe):
        input("\nPress Enter to exit...")
        return
    
    # Install dependencies
    if not install_dependencies():
        input("\nPress Enter to exit...")
        return
    
    # Verify installation
    if not verify_installation():
        print("\n⚠️ Installation verification failed!")
        input("\nPress Enter to exit...")
        return
    
    # Create launcher
    create_launcher()
    
    # Success message
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print("\n🚀 To play the game:")
    if os.name == 'nt':
        print("   • Double-click: play.bat")
        print("   • Or run: .\\venv\\Scripts\\python.exe hand.py")
    else:
        print("   • Run: ./play.sh")
        print("   • Or run: ./venv/bin/python hand.py")
    
    print("\n📋 Game Controls:")
    print("   • Left hand controls left paddle")
    print("   • Right hand controls right paddle")
    print("   • Move hands up/down to control paddles")
    print("   • Press 'q' or 'ESC' to quit")
    
    print("\n🎯 Tips for best experience:")
    print("   • Ensure good lighting")
    print("   • Use plain background")
    print("   • Keep hands clearly visible")
    print("   • Stay 2-3 feet from camera")
    
    input("\n✨ Press Enter to exit setup...")

if __name__ == "__main__":
    main()
