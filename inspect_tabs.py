#!/usr/bin/env python3
"""
Inspect dashboard structure to find navigation tab selectors.
"""
import time
from playwright.sync_api import sync_playwright

USER_DATA_DIR = './browser_data_chromium'
DASHBOARD_URL = 'https://lookerstudio.google.com/u/0/reporting/ae967ece-bc34-426f-97f7-b28f7eae801e/page/p_63dxazbhzc'

def inspect_page_structure():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ],
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        )

        page = context.pages[0] if context.pages else context.new_page()

        print("Navigating to dashboard...")
        page.goto(DASHBOARD_URL, wait_until='load', timeout=60000)
        print("Waiting for content to load...")
        time.sleep(15)

        print("\n" + "="*80)
        print("INSPECTING PAGE STRUCTURE FOR NAVIGATION ELEMENTS")
        print("="*80)

        # Try various selectors that might match the numbered page navigation
        test_selectors = [
            # Page navigation specific
            '[class*="page"]',
            '[class*="navigation"]',
            '[class*="sidebar"]',
            '[aria-label*="page"]',
            '[aria-label*="Page"]',
            'nav',
            'nav a',
            'nav button',
            'nav div',
            # Looker Studio specific
            '[class*="lego"]',
            '[class*="canvas-page"]',
            '[class*="report-page"]',
            # Number indicators
            'div:has-text("1")',
            'button:has-text("2")',
            'a:has-text("3")',
        ]

        for selector in test_selectors:
            try:
                elements = page.query_selector_all(selector)
                if elements:
                    visible_elements = [el for el in elements if el.is_visible()]
                    if visible_elements:
                        print(f"\n✓ '{selector}': Found {len(visible_elements)} visible elements")
                        # Show first 5 elements
                        for i, el in enumerate(visible_elements[:5]):
                            try:
                                text = el.inner_text().strip()
                                aria_label = el.get_attribute('aria-label') or ''
                                class_name = el.get_attribute('class') or ''
                                tag = el.evaluate('el => el.tagName')
                                print(f"   [{i+1}] {tag}: text='{text[:50]}', aria-label='{aria_label[:50]}', class='{class_name[:50]}'")
                            except:
                                pass
            except Exception as e:
                pass

        print("\n" + "="*80)
        print("CHECKING LEFT SIDEBAR AREA")
        print("="*80)

        # Try to get the HTML structure of the left side of the page
        try:
            # Get elements positioned on the left side (x < 100 pixels)
            left_elements = page.evaluate("""() => {
                const elements = Array.from(document.querySelectorAll('*'));
                const leftElements = elements.filter(el => {
                    const rect = el.getBoundingClientRect();
                    return rect.left < 100 && rect.width < 100 && rect.height > 20 && rect.height < 60;
                });
                return leftElements.map(el => ({
                    tag: el.tagName,
                    text: el.innerText?.trim().substring(0, 20),
                    class: el.className,
                    id: el.id,
                    role: el.getAttribute('role'),
                    ariaLabel: el.getAttribute('aria-label')
                }));
            }""")

            print(f"\nFound {len(left_elements)} elements in left sidebar area:")
            for i, el in enumerate(left_elements[:20]):
                print(f"   [{i+1}] {el['tag']}: '{el['text']}' (class: {el['class'][:40]})")
        except Exception as e:
            print(f"Error getting left elements: {e}")

        print("\n" + "="*80)
        input("\nPress Enter to close browser and exit...")
        context.close()

if __name__ == '__main__':
    inspect_page_structure()
