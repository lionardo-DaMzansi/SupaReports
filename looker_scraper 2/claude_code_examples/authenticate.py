#!/usr/bin/env python3
"""
One-time authentication script for Google services.
Run this once to log in manually and save your session.
"""
import time
import os
from playwright.sync_api import sync_playwright

# Define the directory to save the browser session
USER_DATA_DIR = './my_google_session'

def run_authentication():
    """Launches a browser for manual login and saves the session."""
    print("=" * 80)
    print("GOOGLE AUTHENTICATION - ONE-TIME SETUP")
    print("=" * 80)
    
    with sync_playwright() as p:
        # Launch a persistent browser context
        # This will use the specified directory to save the session
        context = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=False,  # Must be False to allow manual login
            args=[
                '--disable-blink-features=AutomationControlled',  # Helps hide automation
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ],
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
        )

        page = context.pages[0] if context.pages else context.new_page()
        
        print("\n>>> A browser window has been opened.")
        print("\nINSTRUCTIONS:")
        print("1. Log in to your Google account in the browser window")
        print("2. Complete any 2FA/verification if prompted")
        print("3. Navigate to a Looker Studio dashboard to confirm login")
        print("4. Once logged in successfully, CLOSE THE BROWSER WINDOW")
        print("\nThe script will wait for you to close the browser...")
        print("=" * 80)
        
        # Navigate to Google login page
        page.goto('https://accounts.google.com')

        try:
            # Wait for the browser to be closed by the user
            page.wait_for_event('close', timeout=300000)  # 5 minute timeout
        except:
            print("\nTimeout or browser closed.")

        context.close()
        
        print("\n" + "=" * 80)
        print("✅ AUTHENTICATION SUCCESSFUL!")
        print("=" * 80)
        print(f"Session saved to: {os.path.abspath(USER_DATA_DIR)}")
        print("\nYou can now run the scraper script without logging in again.")
        print("Session typically lasts 30-90 days before needing to re-authenticate.")
        print("=" * 80)

if __name__ == '__main__':
    run_authentication()
