#!/usr/bin/env python3
"""
Setup script for Letterboxd Sync
This script helps you install dependencies and configure the application.
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required Python packages"""
    print("\nInstalling dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def create_env_file():
    """Create .env file from template"""
    if os.path.exists('.env'):
        print("✓ .env file already exists")
        return
    
    if os.path.exists('env.example'):
        shutil.copy('env.example', '.env')
        print("✓ Created .env file from template")
        print("  Please edit .env file with your configuration")
    else:
        print("⚠ env.example not found, creating basic .env file")
        with open('.env', 'w') as f:
            f.write("# Letterboxd Sync Configuration\n")
            f.write("# Fill in your values below\n\n")
            f.write("LETTERBOXD_USERNAME=your_letterboxd_username\n")
            f.write("PLEX_TOKEN=your_plex_token\n")
            f.write("PLEX_HOST=http://your_plex_server_ip:32400\n")
            f.write("RADARR_TOKEN=your_radarr_api_key\n")
            f.write("RADARR_HOST=http://your_radarr_instance_ip:7878\n")
        print("✓ Created basic .env file")
        print("  Please edit .env file with your configuration")

def test_imports():
    """Test if all modules can be imported"""
    print("\nTesting imports...")
    try:
        import list_scraper
        import plex_watchlist
        import radarr_monitor
        import main
        print("✓ All modules imported successfully")
    except ImportError as e:
        print(f"Error importing modules: {e}")
        sys.exit(1)

def main():
    print("Letterboxd Sync Setup")
    print("=====================")
    
    check_python_version()
    install_dependencies()
    create_env_file()
    test_imports()
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Edit the .env file with your configuration")
    print("2. Run: python3 main.py")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main() 