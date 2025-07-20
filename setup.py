#!/usr/bin/env python3
"""
Setup script for Advanced Chess.com Bot
Installs dependencies and sets up the environment
"""

import os
import sys
import subprocess
import platform
import argparse
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_system_dependencies():
    """Install system dependencies"""
    system = platform.system().lower()
    
    if system == "linux":
        print("Installing system dependencies for Linux...")
        try:
            subprocess.run([
                "sudo", "apt", "update"
            ], check=True, capture_output=True)
            
            subprocess.run([
                "sudo", "apt", "install", "-y",
                "python3-venv", "python3-pip", "python3-dev",
                "build-essential", "libssl-dev", "libffi-dev",
                "google-chrome-stable", "xvfb"
            ], check=True, capture_output=True)
            print("✅ System dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install system dependencies: {e}")
            return False
    
    elif system == "darwin":  # macOS
        print("Installing system dependencies for macOS...")
        try:
            # Check if Homebrew is installed
            result = subprocess.run(["which", "brew"], capture_output=True)
            if result.returncode != 0:
                print("Installing Homebrew...")
                subprocess.run([
                    "/bin/bash", "-c", 
                    '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)'
                ], check=True)
            
            subprocess.run([
                "brew", "install", "python3", "google-chrome"
            ], check=True, capture_output=True)
            print("✅ System dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install system dependencies: {e}")
            return False
    
    elif system == "windows":
        print("For Windows, please install the following manually:")
        print("- Python 3.8+ from python.org")
        print("- Google Chrome from google.com/chrome")
        print("- Visual Studio Build Tools (for some packages)")
        return True
    
    return True

def create_virtual_environment():
    """Create virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def get_pip_command():
    """Get the pip command for the virtual environment"""
    if platform.system().lower() == "windows":
        return "venv\\Scripts\\pip"
    else:
        return "venv/bin/pip"

def get_python_command():
    """Get the python command for the virtual environment"""
    if platform.system().lower() == "windows":
        return "venv\\Scripts\\python"
    else:
        return "venv/bin/python"

def install_python_dependencies():
    """Install Python dependencies"""
    pip_cmd = get_pip_command()
    
    print("Upgrading pip...")
    try:
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to upgrade pip: {e}")
        return False
    
    print("Installing Python dependencies...")
    try:
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✅ Python dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False

def create_config_files():
    """Create default configuration files"""
    config_files = {
        ".env": """# Chess Bot Environment Variables
# Chess.com credentials
CHESS_USERNAME=your_username_here
CHESS_PASSWORD=your_password_here

# Bot settings
GAME_TYPE=rapid
TIME_CONTROL=10+0
DIFFICULTY=intermediate
MAX_GAMES_PER_SESSION=5
SESSION_DURATION_LIMIT=3600

# Browser settings
BROWSER_HEADLESS=false
DISABLE_IMAGES=true
INCOGNITO=true

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=true

# Safety
HUMAN_LIKE_BEHAVIOR=true
""",
        
        "bot_configs.json": """[
  {
    "id": "rapid_bot",
    "username": "your_rapid_username",
    "password": "your_rapid_password",
    "game_type": "rapid",
    "time_control": "10+0",
    "difficulty": "intermediate",
    "max_games": 5,
    "session_duration": 1800,
    "description": "Rapid games bot"
  },
  {
    "id": "blitz_bot",
    "username": "your_blitz_username",
    "password": "your_blitz_password",
    "game_type": "blitz",
    "time_control": "3+0",
    "difficulty": "advanced",
    "max_games": 10,
    "session_duration": 3600,
    "description": "Blitz games bot"
  }
]""",
        
        "run_bot.sh": """#!/bin/bash
# Script to run the chess bot
source venv/bin/activate

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run the bot
python advanced_chess_bot.py \\
    --username "$CHESS_USERNAME" \\
    --password "$CHESS_PASSWORD" \\
    --game-type "$GAME_TYPE" \\
    --time-control "$TIME_CONTROL" \\
    --difficulty "$DIFFICULTY" \\
    --max-games "$MAX_GAMES_PER_SESSION" \\
    --session-duration "$SESSION_DURATION_LIMIT"
""",
        
        "run_manager.sh": """#!/bin/bash
# Script to run the bot manager
source venv/bin/activate

# Run the bot manager
python bot_manager.py --config bot_configs.json --web-port 8080
""",
        
        "run_analysis.sh": """#!/bin/bash
# Script to run analysis tools
source venv/bin/activate

# Analyze performance
python analysis_tools.py --mode performance --input . --output performance_report.txt --charts

# Analyze openings
python analysis_tools.py --mode openings --input . --output opening_report.txt
"""
    }
    
    for filename, content in config_files.items():
        if not Path(filename).exists():
            with open(filename, 'w') as f:
                f.write(content)
            print(f"✅ Created {filename}")
        else:
            print(f"⚠️  {filename} already exists, skipping")

def make_scripts_executable():
    """Make shell scripts executable (Unix-like systems)"""
    if platform.system().lower() != "windows":
        scripts = ["run_bot.sh", "run_manager.sh", "run_analysis.sh"]
        for script in scripts:
            if Path(script).exists():
                os.chmod(script, 0o755)
                print(f"✅ Made {script} executable")

def test_installation():
    """Test the installation"""
    python_cmd = get_python_command()
    
    print("Testing installation...")
    
    # Test imports
    test_script = """
import sys
import chess
import selenium
import flask
import matplotlib
import numpy
import psutil
from config import config
print("✅ All imports successful")
"""
    
    try:
        result = subprocess.run([python_cmd, "-c", test_script], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout.strip())
            return True
        else:
            print(f"❌ Import test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Edit .env file with your Chess.com credentials")
    print("2. Edit bot_configs.json with your bot configurations")
    print("3. Run the bot:")
    print("   - Single bot: ./run_bot.sh")
    print("   - Bot manager: ./run_manager.sh")
    print("   - Analysis: ./run_analysis.sh")
    print("\nOr run manually:")
    print("   source venv/bin/activate")
    print("   python advanced_chess_bot.py --username YOUR_USERNAME --password YOUR_PASSWORD")
    print("\nFor help:")
    print("   python advanced_chess_bot.py --help")
    print("   python bot_manager.py --help")
    print("   python analysis_tools.py --help")

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="Setup script for Chess Bot")
    parser.add_argument("--skip-system", action="store_true", help="Skip system dependencies")
    parser.add_argument("--skip-venv", action="store_true", help="Skip virtual environment creation")
    parser.add_argument("--skip-deps", action="store_true", help="Skip Python dependencies")
    parser.add_argument("--skip-config", action="store_true", help="Skip config file creation")
    parser.add_argument("--test-only", action="store_true", help="Only run tests")
    
    args = parser.parse_args()
    
    print("🚀 Setting up Advanced Chess.com Bot")
    print("="*50)
    
    if args.test_only:
        if test_installation():
            print("✅ Installation test passed")
        else:
            print("❌ Installation test failed")
        return
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install system dependencies
    if not args.skip_system:
        if not install_system_dependencies():
            print("⚠️  System dependency installation failed, continuing...")
    
    # Create virtual environment
    if not args.skip_venv:
        if not create_virtual_environment():
            sys.exit(1)
    
    # Install Python dependencies
    if not args.skip_deps:
        if not install_python_dependencies():
            sys.exit(1)
    
    # Create config files
    if not args.skip_config:
        create_config_files()
        make_scripts_executable()
    
    # Test installation
    if test_installation():
        print_next_steps()
    else:
        print("❌ Installation test failed")
        sys.exit(1)

if __name__ == "__main__":
    main()