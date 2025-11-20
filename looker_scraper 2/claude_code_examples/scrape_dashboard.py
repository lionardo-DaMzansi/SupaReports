#!/usr/bin/env python3
"""
Looker Studio Dashboard Scraper
Uses saved authentication session to scrape dashboards without login prompts.
"""
import time
import json
from playwright.sync_api import sync_playwright

# Use the same directory where the session was saved
USER_DATA_DIR = './my_google_session'

def scrape_looker_studio(url: str, wait_time: int = 15):
    """
    Scrapes a Looker Studio dashboard using the saved session.
    
    Args:
        url: The URL of the Looker Studio dashboard
        wait_time: Time to wait for dashboard to fully load (seconds)
    
    Returns:
        Dictionary with extracted data or None if failed
    """
    print("=" * 80)
    print(f"SCRAPING DASHBOARD")
    print("=" * 80)
    print(f"URL: {url}")
    print(f"Wait time: {wait_time}s")
    print("=" * 80)
    
    with sync_playwright() as p:
        # Launch a browser using the saved session
        context = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=True,  # Set to False for debugging
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ],
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        )

        page = context.pages[0] if context.pages else context.new_page()

        try:
            print("\n[1/4] Navigating to dashboard...")
            page.goto(url, wait_until='networkidle', timeout=90000)
            
            # Check if login is still required (e.g., session expired)
            if 'accounts.google.com' in page.url:
                print("\n❌ ERROR: Session has expired or is invalid.")
                print("Please run 'python authenticate.py' again to refresh your session.")
                context.close()
                return None

            print("✅ Dashboard loaded successfully")
            print(f"Title: {page.title()}")

            # Wait for the dashboard to fully render
            print(f"\n[2/4] Waiting {wait_time}s for dashboard to render...")
            time.sleep(wait_time)

            print("\n[3/4] Extracting data...")
            
            # Extract all text content from the page
            dashboard_content = page.inner_text('body')
            
            # Take a screenshot for verification
            screenshot_path = f'dashboard_screenshot_{int(time.time())}.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"✅ Screenshot saved: {screenshot_path}")

            # --- CUSTOM DATA EXTRACTION LOGIC ---
            # You can add more specific extraction here
            # For example, extracting specific metrics, tables, etc.
            
            # Example: Try to find metric values
            metrics = {}
            try:
                # This is a simplified example - adjust selectors based on actual dashboard
                all_text = dashboard_content.split('\n')
                for i, line in enumerate(all_text):
                    if 'CPM' in line and i + 1 < len(all_text):
                        metrics['CPM'] = all_text[i + 1]
                    elif 'CPC' in line and i + 1 < len(all_text):
                        metrics['CPC'] = all_text[i + 1]
                    elif 'CTR' in line and i + 1 < len(all_text):
                        metrics['CTR'] = all_text[i + 1]
                    elif 'Spend' in line and i + 1 < len(all_text):
                        metrics['Spend'] = all_text[i + 1]
            except Exception as e:
                print(f"Note: Could not extract specific metrics: {e}")
            
            # ------------------------------------

            result = {
                'status': 'success',
                'url': url,
                'title': page.title(),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'screenshot': screenshot_path,
                'content_length': len(dashboard_content),
                'content_preview': dashboard_content[:2000],  # First 2000 chars
                'metrics': metrics
            }

            print("\n[4/4] Extraction complete!")
            print(f"✅ Content length: {len(dashboard_content)} characters")
            if metrics:
                print(f"✅ Metrics extracted: {list(metrics.keys())}")

            context.close()
            return result

        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            import traceback
            traceback.print_exc()
            context.close()
            return None


def save_results(data: dict, filename: str = 'scrape_results.json'):
    """Save scraping results to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n✅ Results saved to: {filename}")


if __name__ == '__main__':
    # Example usage
    dashboard_url = 'https://lookerstudio.google.com/reporting/0d09cdb0-cb51-479f-bf60-0214fc2ea40f/page/XQqUC'
    
    # Scrape the dashboard
    results = scrape_looker_studio(dashboard_url, wait_time=15)
    
    if results:
        # Save results to file
        save_results(results)
        
        # Print summary
        print("\n" + "=" * 80)
        print("SCRAPING SUMMARY")
        print("=" * 80)
        print(f"Status: {results['status']}")
        print(f"Dashboard: {results['title']}")
        print(f"Timestamp: {results['timestamp']}")
        print(f"Content extracted: {results['content_length']} characters")
        if results.get('metrics'):
            print("\nExtracted Metrics:")
            for key, value in results['metrics'].items():
                print(f"  {key}: {value}")
        print("=" * 80)
    else:
        print("\n❌ Scraping failed. Please check the errors above.")
