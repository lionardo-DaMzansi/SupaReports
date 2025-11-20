#!/usr/bin/env python3
"""
Simple OCR test - just load page and run OCR on first view
"""
import time
from playwright.sync_api import sync_playwright
from looker_extractor import LookerStudioExtractor

DASHBOARD_URL = "https://lookerstudio.google.com/u/0/reporting/8cc1c84c-0bfa-4700-b8ce-3077f8990860/page/p_sbasoctahd"

print("=" * 80)
print("SIMPLE OCR TEST")
print("=" * 80)

with sync_playwright() as p:
    print("🌐 Launching browser (non-headless for visibility)...")
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()

    print(f"📄 Navigating to: {DASHBOARD_URL}")
    page.goto(DASHBOARD_URL, wait_until='load', timeout=60000)
    print(f"✓ Page loaded: {page.title()}")

    # Wait for content
    print("⏳ Waiting 30 seconds for dashboard to fully load...")
    time.sleep(30)

    # Create extractor
    extractor = LookerStudioExtractor(page)

    # Run just ONE OCR extraction
    print("\n📸 Running OCR extraction on current view...")
    ocr_result = extractor.extract_text_via_ocr()

    print("\n" + "=" * 80)
    print("RESULTS:")
    print("=" * 80)
    if ocr_result.get('extracted_text'):
        text = ocr_result['extracted_text']
        print(f"Characters extracted: {ocr_result.get('character_count', 0)}")
        print(f"Lines extracted: {ocr_result.get('lines_extracted', 0)}")
        print("\nExtracted Text:")
        print("-" * 80)
        print(text[:1000])  # First 1000 characters
        if len(text) > 1000:
            print(f"\n... ({len(text) - 1000} more characters)")

        # Save to file
        with open('simple_ocr_results.txt', 'w') as f:
            f.write(text)
        print(f"\n✓ Full text saved to: simple_ocr_results.txt")
    else:
        print("❌ No text extracted")
        if 'error' in ocr_result:
            print(f"Error: {ocr_result['error']}")

    browser.close()
    print("\n✓ Test complete!")
