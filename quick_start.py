#!/usr/bin/env python3
"""
Quick Start Script for Chess.com Bot
This script helps you get the bot running quickly
"""

import os
import sys
import subprocess
import getpass

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        'selenium',
        'chess',
        'webdriver-manager',
        'pillow',
        'tqdm'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    print("✓ All dependencies are installed!")
    return True

def check_files():
    """Check if required files exist"""
    print("\nChecking required files...")
    
    required_files = [
        'simple_chess_bot.py',
        'config.py',
        'sunfish.py',
        'requirements.txt'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} (missing)")
            missing_files.append(file)
    
    if missing_files:
        print(f"\nMissing files: {', '.join(missing_files)}")
        return False
    
    print("✓ All required files are present!")
    return True

def get_credentials():
    """Get Chess.com credentials from user"""
    print("\nChess.com Credentials")
    print("=" * 30)
    
    username = input("Enter your Chess.com username: ").strip()
    password = getpass.getpass("Enter your Chess.com password: ").strip()
    
    if not username or not password:
        print("Username and password are required!")
        return None, None
    
    return username, password

def get_game_settings():
    """Get game settings from user"""
    print("\nGame Settings")
    print("=" * 30)
    
    print("Available time controls:")
    print("1. 10+0 (10 minutes, no increment)")
    print("2. 5+0 (5 minutes, no increment)")
    print("3. 3+0 (3 minutes, no increment)")
    print("4. 1+0 (1 minute, no increment)")
    print("5. Custom")
    
    choice = input("Select time control (1-5): ").strip()
    
    time_controls = {
        '1': '10+0',
        '2': '5+0',
        '3': '3+0',
        '4': '1+0'
    }
    
    if choice in time_controls:
        time_control = time_controls[choice]
    elif choice == '5':
        time_control = input("Enter custom time control (e.g., 5+3): ").strip()
    else:
        print("Invalid choice, using default (10+0)")
        time_control = '10+0'
    
    headless = input("Run in headless mode? (y/n): ").strip().lower() == 'y'
    
    return time_control, headless

def run_bot(username, password, time_control, headless):
    """Run the chess bot"""
    print(f"\nStarting bot with settings:")
    print(f"Username: {username}")
    print(f"Time control: {time_control}")
    print(f"Headless: {headless}")
    print("=" * 40)
    
    # Build command
    cmd = [
        sys.executable, 'simple_chess_bot.py',
        '--username', username,
        '--password', password,
        '--time-control', time_control
    ]
    
    if headless:
        cmd.append('--headless')
    
    try:
        # Run the bot
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Bot exited with error code {e.returncode}")
    except KeyboardInterrupt:
        print("\nBot stopped by user")

def main():
    """Main function"""
    print("Chess.com Bot - Quick Start")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install missing dependencies first.")
        return
    
    # Check files
    if not check_files():
        print("\nPlease ensure all required files are present.")
        return
    
    # Get credentials
    username, password = get_credentials()
    if not username or not password:
        return
    
    # Get game settings
    time_control, headless = get_game_settings()
    
    # Confirm settings
    print(f"\nBot will start with these settings:")
    print(f"Username: {username}")
    print(f"Time control: {time_control}")
    print(f"Headless mode: {headless}")
    
    confirm = input("\nStart the bot? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Bot startup cancelled.")
        return
    
    # Run the bot
    run_bot(username, password, time_control, headless)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuick start cancelled.")
    except Exception as e:
        print(f"Error: {e}")