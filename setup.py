"""
Automatic Setup Script for Hand Gesture Controlled Ping Pong Game
This script will:
1. Find compatible Python version (3.11, 3.12, or 3.13)
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
    """Find a compatible Python version (3.11, 3.12, or 3.13) on the system"""
    print("🔍 Searching for compatible Python version...")
    
    # Check current Python
    current_version = sys.version_info
    print(f"   Current Python: {current_version.major}.{current_version.minor}.{current_version.micro}")
    
    if current_version.major == 3 and current_version.minor in [11, 12, 13]:
        print(f"✅ Current Python {current_version.major}.{current_version.minor} is compatible!")
        return sys.executable
    
    # Try to find other Python versions
    possible_commands = [
        'py -3.13',
        'py -3.12',
        'py -3.11', 
        'python3.13',
        'python3.12',
        'python3.11',
        'python313',
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
    
    print("\n⚠️ No compatible Python version found (3.11, 3.12, or 3.13)")
    print("📥 Please install Python 3.13 from: https://www.python.org/downloads/")
    print("   Make sure to check 'Add Python to PATH' during installation")
    return None

def check_existing_venv():
    """Check if a working virtual environment already exists"""
    venv_python = get_venv_python()
    
    if not os.path.exists(venv_python):
        return False
    
    print("\n🔍 Found existing virtual environment, checking if it works...")
    
    # Test if venv works by importing key packages
    test_code = """
import sys
try:
    import cv2
    import mediapipe
    import PIL
    import numpy
    sys.exit(0)
except ImportError:
    sys.exit(1)
"""
    
    try:
        result = subprocess.run(
            [venv_python, '-c', test_code],
            capture_output=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✅ Existing virtual environment is working!")
            return True
        else:
            print("⚠️ Existing virtual environment has missing packages")
            return False
    except Exception:
        print("⚠️ Existing virtual environment is not working")
        return False

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



def verify_installation():
    """Verify that all packages are properly installed"""
    print("\n🔍 Verifying installation...")
    venv_python = get_venv_python()
    
    test_code = """
import sys
success = True
errors = []

try:
    import cv2
    print(f"✅ OpenCV: {cv2.__version__}")
except ImportError as e:
    print(f"❌ OpenCV import failed: {e}")
    errors.append(str(e))
    success = False

try:
    import mediapipe
    print(f"✅ MediaPipe: {mediapipe.__version__}")
except ImportError as e:
    print(f"❌ MediaPipe import failed: {e}")
    errors.append(str(e))
    success = False

try:
    import PIL
    print(f"✅ Pillow imported successfully")
except ImportError as e:
    print(f"❌ Pillow import failed: {e}")
    errors.append(str(e))
    success = False

try:
    import numpy
    print(f"✅ NumPy: {numpy.__version__}")
except ImportError as e:
    print(f"❌ NumPy import failed: {e}")
    errors.append(str(e))
    success = False

if success:
    print("\\n✅ All packages verified successfully!")
    sys.exit(0)
else:
    print("\\n❌ Some packages failed to import")
    sys.exit(1)
"""
    
    try:
        result = subprocess.run(
            [venv_python, '-c', test_code],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Print all output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⚠️ Verification timed out")
        return False
    except Exception as e:
        print(f"⚠️ Verification failed with exception: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("🏓 Hand Gesture Controlled Ping Pong Game - Automatic Setup")
    print("=" * 60)
    
    # Check if venv already exists and works
    if check_existing_venv():
        print("\n✨ Virtual environment already set up and working!")
        
      
        
        print("\n" + "=" * 60)
        print("🎉 READY TO PLAY!")
        print("=" * 60)
        
        
        print("\n💡 To reinstall dependencies, delete the 'venv' folder and run setup again.")
        
        return
    
    # Find compatible Python
    python_exe = find_python_executable()
    if not python_exe:
        
        return
    
    # Create virtual environment
    if not create_venv(python_exe):
        
        return
    
    # Install dependencies
    if not install_dependencies():
        
        return
    
    # Verify installation
    verification_passed = verify_installation()
    
   
    
    # Success message
    print("\n" + "=" * 60)
    if verification_passed:
        print("🎉 SETUP COMPLETE!")
    else:
        print("⚠️ SETUP COMPLETE (with warnings)")
        print("   Dependencies installed but verification had issues.")
        print("   Try running the game anyway - it might still work!")
    print("=" * 60)
    
    
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
    
    

if __name__ == "__main__":
    main()