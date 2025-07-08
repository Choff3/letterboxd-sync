#!/usr/bin/env python3
"""
Test script for Letterboxd Sync
This script tests the basic functionality without making any external API calls.
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test environment variable loading"""
    print("Testing environment variables...")
    load_dotenv()
    
    username = os.getenv('LETTERBOXD_USERNAME')
    if username and username != 'your_letterboxd_username':
        print(f"✓ LETTERBOXD_USERNAME is set to: {username}")
    else:
        print("⚠ LETTERBOXD_USERNAME not configured (required)")
    
    plex_token = os.getenv('PLEX_TOKEN')
    plex_host = os.getenv('PLEX_HOST')
    if plex_token and plex_host and plex_token != 'your_plex_token':
        print("✓ Plex configuration found")
    else:
        print("⚠ Plex not configured (optional)")
    
    radarr_token = os.getenv('RADARR_TOKEN')
    radarr_host = os.getenv('RADARR_HOST')
    if radarr_token and radarr_host and radarr_token != 'your_radarr_api_key':
        print("✓ Radarr configuration found")
    else:
        print("⚠ Radarr not configured (optional)")

def test_modules():
    """Test module imports"""
    print("\nTesting module imports...")
    try:
        import list_scraper
        print("✓ list_scraper imported")
    except ImportError as e:
        print(f"✗ Error importing list_scraper: {e}")
    
    try:
        import plex_watchlist
        print("✓ plex_watchlist imported")
    except ImportError as e:
        print(f"✗ Error importing plex_watchlist: {e}")
    
    try:
        import radarr_monitor
        print("✓ radarr_monitor imported")
    except ImportError as e:
        print(f"✗ Error importing radarr_monitor: {e}")

def test_dependencies():
    """Test external dependencies"""
    print("\nTesting external dependencies...")
    try:
        import requests
        print("✓ requests imported")
    except ImportError as e:
        print(f"✗ Error importing requests: {e}")
    
    try:
        import bs4
        print("✓ bs4 imported")
    except ImportError as e:
        print(f"✗ Error importing bs4: {e}")
    
    try:
        import plexapi
        print("✓ plexapi imported")
    except ImportError as e:
        print(f"✗ Error importing plexapi: {e}")
    
    try:
        import tqdm
        print("✓ tqdm imported")
    except ImportError as e:
        print(f"✗ Error importing tqdm: {e}")

def main():
    print("Letterboxd Sync Test")
    print("===================")
    
    test_environment()
    test_modules()
    test_dependencies()
    
    print("\nTest completed!")
    print("\nIf all tests passed, you can run the main script with:")
    print("python3 main.py")

if __name__ == "__main__":
    main() 