#!/usr/bin/env python3
"""
Google Authentication Setup for Looker Studio Dashboard Scraping

This script opens a browser window for you to log in to Google once.
Your authentication session will be saved and reused for future dashboard scraping.

Usage:
    python3 setup_google_auth.py [browser]

Arguments:
    browser (optional): chromium, firefox, or webkit (default: firefox)
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

def setup_google_authentication(browser_type='firefox'):
    """
    Open a browser for manual Google login and save the authentication state.

    Args:
        browser_type: 'chromium', 'firefox', or 'webkit' (default: firefox)
    """
    print("=" * 70)
    print("Google Authentication Setup for Looker Studio")
    print("=" * 70)
    print()
    print(f"This will open a {browser_type.capitalize()} browser window.")
    print("Please log in to your Google account that has access to Looker Studio.")
    print()
    print("Steps:")
    print("  1. A browser window will open")
    print("  2. Log in to Google")
    print("  3. Navigate to one of your Looker Studio dashboards to verify access")
    print("  4. Press Enter in this terminal when you're done")
    print()

    # Path to store browser authentication data for the specific browser
    auth_dir = os.path.join(os.path.dirname(__file__), f'browser_data_{browser_type}')
    os.makedirs(auth_dir, exist_ok=True)

    print(f"📁 Authentication data will be saved to: {auth_dir}")
    print()

    input("Press Enter to open the browser...")
    print()

    with sync_playwright() as p:
        # Select the browser
        if browser_type == 'firefox':
            browser = p.firefox
        elif browser_type == 'webkit':
            browser = p.webkit
        else:  # chromium
            browser = p.chromium

        # Launch persistent context in NON-headless mode for manual login
        print(f"🌐 Opening {browser_type.capitalize()} browser...")

        # Browser arguments to bypass Google's automation detection
        browser_args = [
            '--disable-blink-features=AutomationControlled',  # Hide automation
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-site-isolation-trials'
        ]

        context = browser.launch_persistent_context(
            auth_dir,
            headless=False,  # Must be visible for login
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            args=browser_args if browser_type == 'chromium' else []
        )

        # Use existing page if available (persistent context may have one)
        page = context.pages[0] if context.pages else context.new_page()

        # Remove webdriver property to hide automation
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );

            // Hide Chrome headless
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)

        # Navigate to Google to trigger login
        print("📍 Navigating to Google...")
        page.goto('https://accounts.google.com')

        print()
        print("=" * 70)
        print("✅ Browser opened successfully!")
        print()
        print(">>> Please complete these steps in the browser:")
        print("  1. Log in to your Google account")
        print("  2. Complete any 2FA verification if prompted")
        print("  3. Navigate to: https://lookerstudio.google.com")
        print("  4. Open one of your dashboards to verify you can access it")
        print("  5. CLOSE THE BROWSER WINDOW when done")
        print()
        print(">>> The script will wait here until you close the browser...")
        print("=" * 70)
        print()

        # Wait for the user to close the browser window
        # This is the KEY difference - don't use input(), wait for browser close
        try:
            page.wait_for_event('close', timeout=300000)  # 5 minute timeout
        except:
            print("\nTimeout or browser closed.")

        print()
        print("💾 Browser closed. Saving authentication state...")

        context.close()

        print()
        print("=" * 70)
        print("✅ Authentication setup complete!")
        print()
        print("Your Google session has been saved.")
        print("Future dashboard scraping will use this authenticated session.")
        print()
        print("You can now submit dashboard links in the Supa Reports app.")
        print("=" * 70)
        print()

        return True

if __name__ == '__main__':
    # Get browser choice from command line or use default (chromium)
    browser_type = 'chromium'  # Default to Chromium (matches Manus examples)

    if len(sys.argv) > 1:
        browser_arg = sys.argv[1].lower()
        if browser_arg in ['chromium', 'firefox', 'webkit']:
            browser_type = browser_arg
        else:
            print(f"❌ Invalid browser: {sys.argv[1]}")
            print("Valid options: chromium, firefox, webkit")
            print()
            print("Usage: python3 setup_google_auth.py [browser]")
            print("Example: python3 setup_google_auth.py firefox")
            exit(1)

    try:
        setup_google_authentication(browser_type)
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Error during setup: {e}")
        print("\nPlease try again or contact support if the issue persists.")
        print()
        print("💡 Tip: Try a different browser:")
        print("   python3 setup_google_auth.py firefox")
        print("   python3 setup_google_auth.py webkit")
        print("   python3 setup_google_auth.py chromium")
        exit(1)
