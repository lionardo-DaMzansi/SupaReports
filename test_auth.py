#!/usr/bin/env python3
"""
Quick test to verify Chromium authentication works.
Based on Manus's exact working methodology.
"""
import time
from playwright.sync_api import sync_playwright
from looker_extractor import LookerStudioExtractor

USER_DATA_DIR = './browser_data_chromium'

def test_scrape(url):
    """Test scraping with saved session."""
    print("=" * 80)
    print("TESTING AUTHENTICATED SCRAPING")
    print("=" * 80)
    print(f"URL: {url}")
    print(f"Session: {USER_DATA_DIR}")
    print("=" * 80)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=False,  # Set to False to watch what happens
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
            print(f"      Target URL: {url}")

            # Use 'load' instead of 'networkidle' - Looker dashboards never reach networkidle
            # because they continuously fetch data in the background
            page.goto(url, wait_until='load', timeout=60000)

            print(f"      Current URL: {page.url}")
            print(f"      Page title: {page.title()}")

            # Check if login required
            if 'accounts.google.com' in page.url:
                print("\n❌ ERROR: Redirected to Google login!")
                print("      This means authentication failed or session expired")
                print("      Run: python3 setup_google_auth.py chromium")

                input("\nPress Enter to close the browser and exit...")
                context.close()
                return False

            # Check if we're on the right page
            if 'lookerstudio.google.com' not in page.url:
                print(f"\n⚠️  WARNING: Unexpected URL: {page.url}")
                print("      Expected: lookerstudio.google.com")

            print("✅ Dashboard loaded!")
            print(f"   Title: {page.title()}")

            print("\n[2/4] Waiting for dashboard to render...")
            print("      (Watch the browser window - data should be loading)")

            # Use LookerStudioExtractor to properly extract dashboard data
            extractor = LookerStudioExtractor(page)

            print("\n[3/4] Extracting dashboard data...")
            try:
                # Extract using Looker-specific selectors with navigation exploration
                # This will click through tabs to get all data
                data = extractor.extract_all_data(explore_nav=True)

                tables_count = len(data.get('tables', []))
                metrics_count = len(data.get('metrics', []))
                charts_count = len(data.get('charts', []))
                filters_count = len(data.get('filters', []))
                ocr_extractions = len(data.get('ocr_text', []))
                ocr_chars = data.get('summary', {}).get('total_ocr_characters', 0)

                print(f"      ✅ Tables extracted: {tables_count}")
                print(f"      ✅ Metrics extracted: {metrics_count}")
                print(f"      ✅ Charts extracted: {charts_count}")
                print(f"      ✅ Filters extracted: {filters_count}")
                print(f"      ✅ OCR extractions: {ocr_extractions} ({ocr_chars} chars)")

                # Also try basic text extraction for comparison
                basic_content = page.inner_text('body')
                print(f"      ✅ Basic text content: {len(basic_content)} characters")

                # Calculate success
                total_data_points = tables_count + metrics_count + charts_count + ocr_extractions

                if total_data_points == 0:
                    print(f"\n⚠️  WARNING: No data extracted!")
                    print("      This might mean:")
                    print("      - Dashboard is still loading (try waiting longer)")
                    print("      - Dashboard structure is different than expected")
                    print("      - Authentication failed silently")

                print(f"\n[4/4] Extraction Summary:")
                print(f"✅ Total data points: {total_data_points}")
                print(f"✅ Dashboard title: {data.get('metadata', {}).get('title', 'N/A')}")

                # Show which tabs were explored
                if data.get('navigation_explored'):
                    print(f"\n🗂️  Tabs explored ({len(data['navigation_explored'])}):")
                    for tab in data['navigation_explored']:
                        print(f"   - {tab}")

                # Show sample of extracted data
                if data.get('metrics'):
                    print(f"\n📊 Sample metrics:")
                    for metric in data['metrics'][:3]:
                        print(f"   - {metric.get('metric_name', 'N/A')}: {metric.get('metric_value', 'N/A')}")

                if data.get('tables'):
                    print(f"\n📋 Sample table data:")
                    table = data['tables'][0]
                    print(f"   - Table with {table.get('row_count', 0)} rows, {table.get('column_count', 0)} columns")
                    if table.get('headers'):
                        print(f"   - Headers: {', '.join(table['headers'][:5])}")

                if data.get('ocr_text'):
                    print(f"\n🔍 Sample OCR extracted text:")
                    for ocr_item in data['ocr_text'][:2]:  # Show first 2 OCR extractions
                        source = ocr_item.get('source', 'unknown')
                        text = ocr_item.get('text', '')
                        print(f"   [{source}] First 200 chars: {text[:200]}...")

            except Exception as extract_error:
                print(f"      ❌ Data extraction failed: {extract_error}")
                import traceback
                traceback.print_exc()
                total_data_points = 0

            # Take a screenshot for debugging
            screenshot_path = f'test_screenshot_{int(time.time())}.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"\n📸 Screenshot saved: {screenshot_path}")

            # Allow user to inspect if running interactively
            import sys
            if sys.stdin.isatty():
                input("\n⏸️  Press Enter to close the browser and finish test...")
            else:
                print("\n⏸️  Waiting 5 seconds before closing browser...")
                time.sleep(5)

            context.close()

            # Pass if we extracted any meaningful data
            return total_data_points > 0

        except Exception as e:
            print(f"\n❌ EXCEPTION OCCURRED!")
            print(f"   Error type: {type(e).__name__}")
            print(f"   Error message: {e}")
            print(f"   Current URL: {page.url if page else 'N/A'}")
            import traceback
            print("\nFull traceback:")
            traceback.print_exc()

            # Allow user to inspect if running interactively
            import sys
            if sys.stdin.isatty():
                input("\n⏸️  Press Enter to close the browser and exit...")
            else:
                print("\n⏸️  Waiting 5 seconds before closing browser...")
                time.sleep(5)

            context.close()
            return False

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        dashboard_url = sys.argv[1]
    else:
        print("Usage: python3 test_auth.py <dashboard_url>")
        print("\nExample:")
        print("  python3 test_auth.py 'https://lookerstudio.google.com/reporting/...'")
        sys.exit(1)

    success = test_scrape(dashboard_url)

    if success:
        print("\n" + "=" * 80)
        print("✅ AUTHENTICATION TEST PASSED!")
        print("Your session is working. You can now use the main app.")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ AUTHENTICATION TEST FAILED")
        print("Please run: python3 setup_google_auth.py chromium")
        print("=" * 80)
