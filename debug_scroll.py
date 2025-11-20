#!/usr/bin/env python3
"""
Debug script to check scroll dimensions and direction
"""
import time
from playwright.sync_api import sync_playwright

USER_DATA_DIR = './browser_data_chromium'
DASHBOARD_URL = 'https://lookerstudio.google.com/u/0/reporting/ae967ece-bc34-426f-97f7-b28f7eae801e/page/p_63dxazbhzc'

def debug_scroll_dimensions():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox'],
            viewport={'width': 1920, 'height': 1080}
        )

        page = context.pages[0] if context.pages else context.new_page()

        print("Loading dashboard...")
        page.goto(DASHBOARD_URL, wait_until='load', timeout=60000)
        time.sleep(20)  # Wait for full load

        print("\n" + "="*80)
        print("SCROLL DIMENSION DEBUG")
        print("="*80)

        # Check window scroll dimensions
        scroll_info = page.evaluate("""
            () => ({
                window: {
                    scrollWidth: window.document.documentElement.scrollWidth,
                    scrollHeight: window.document.documentElement.scrollHeight,
                    clientWidth: window.document.documentElement.clientWidth,
                    clientHeight: window.document.documentElement.clientHeight,
                    scrollX: window.scrollX,
                    scrollY: window.scrollY
                },
                body: {
                    scrollWidth: document.body.scrollWidth,
                    scrollHeight: document.body.scrollHeight,
                    clientWidth: document.body.clientWidth,
                    clientHeight: document.body.clientHeight,
                    overflow: window.getComputedStyle(document.body).overflow,
                    overflowX: window.getComputedStyle(document.body).overflowX,
                    overflowY: window.getComputedStyle(document.body).overflowY
                },
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                }
            })
        """)

        print("\n🪟 WINDOW/DOCUMENT:")
        print(f"   Scroll Size: {scroll_info['window']['scrollWidth']}w x {scroll_info['window']['scrollHeight']}h")
        print(f"   Client Size: {scroll_info['window']['clientWidth']}w x {scroll_info['window']['clientHeight']}h")
        print(f"   Current Scroll: X={scroll_info['window']['scrollX']}, Y={scroll_info['window']['scrollY']}")

        vertical_scrollable = scroll_info['window']['scrollHeight'] > scroll_info['window']['clientHeight']
        horizontal_scrollable = scroll_info['window']['scrollWidth'] > scroll_info['window']['clientWidth']

        print(f"   ✓ Vertically scrollable: {vertical_scrollable}")
        print(f"   ✓ Horizontally scrollable: {horizontal_scrollable}")

        print("\n🧱 BODY:")
        print(f"   Scroll Size: {scroll_info['body']['scrollWidth']}w x {scroll_info['body']['scrollHeight']}h")
        print(f"   Client Size: {scroll_info['body']['clientWidth']}w x {scroll_info['body']['clientHeight']}h")
        print(f"   Overflow: {scroll_info['body']['overflow']}")
        print(f"   OverflowX: {scroll_info['body']['overflowX']}")
        print(f"   OverflowY: {scroll_info['body']['overflowY']}")

        print("\n📐 VIEWPORT:")
        print(f"   Size: {scroll_info['viewport']['width']}w x {scroll_info['viewport']['height']}h")

        # Check for scrollable containers
        print("\n🔍 LOOKING FOR SCROLLABLE CONTAINERS:")
        containers = page.evaluate("""
            () => {
                const allElements = Array.from(document.querySelectorAll('*'));
                const scrollableContainers = allElements.filter(el => {
                    const style = window.getComputedStyle(el);
                    const hasVerticalScroll = el.scrollHeight > el.clientHeight;
                    const hasHorizontalScroll = el.scrollWidth > el.clientWidth;
                    const isScrollable = (style.overflow === 'auto' || style.overflow === 'scroll' ||
                                         style.overflowY === 'auto' || style.overflowY === 'scroll' ||
                                         style.overflowX === 'auto' || style.overflowX === 'scroll');

                    return isScrollable && (hasVerticalScroll || hasHorizontalScroll);
                });

                return scrollableContainers.slice(0, 10).map(el => ({
                    tag: el.tagName,
                    class: el.className.substring(0, 50),
                    id: el.id,
                    scrollWidth: el.scrollWidth,
                    scrollHeight: el.scrollHeight,
                    clientWidth: el.clientWidth,
                    clientHeight: el.clientHeight,
                    overflowY: window.getComputedStyle(el).overflowY,
                    overflowX: window.getComputedStyle(el).overflowX
                }));
            }
        """)

        if containers:
            for i, container in enumerate(containers, 1):
                print(f"\n   Container {i}:")
                print(f"      Tag: {container['tag']}")
                print(f"      Class: {container['class']}")
                print(f"      ID: {container['id']}")
                print(f"      Scroll Size: {container['scrollWidth']}w x {container['scrollHeight']}h")
                print(f"      Client Size: {container['clientWidth']}w x {container['clientHeight']}h")
                print(f"      Overflow: X={container['overflowX']}, Y={container['overflowY']}")

                v_scroll = container['scrollHeight'] > container['clientHeight']
                h_scroll = container['scrollWidth'] > container['clientWidth']
                print(f"      Can scroll: Vertical={v_scroll}, Horizontal={h_scroll}")
        else:
            print("   No scrollable containers found!")

        print("\n" + "="*80)
        print("TEST: Try scrolling window vertically")
        print("="*80)

        # Try to scroll vertically
        page.evaluate("window.scrollTo(0, 500)")
        time.sleep(2)

        new_y = page.evaluate("window.scrollY")
        print(f"   Scrolled to Y=500, actual position: Y={new_y}")

        if new_y == 0:
            print("   ❌ Vertical scroll FAILED - window is NOT vertically scrollable!")
        else:
            print("   ✅ Vertical scroll SUCCESS!")

        # Scroll back to top
        page.evaluate("window.scrollTo(0, 0)")

        print("\n" + "="*80)
        input("\nPress Enter to close...")
        context.close()

if __name__ == '__main__':
    debug_scroll_dimensions()
