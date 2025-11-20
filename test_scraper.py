#!/usr/bin/env python3
"""
Test script for dashboard scraper
Tests the Looker Studio extractor with a specific dashboard URL
"""
import os
import sys
import json
from playwright.sync_api import sync_playwright
from looker_extractor import LookerStudioExtractor
import time

# Test URL
DASHBOARD_URL = "https://lookerstudio.google.com/u/0/reporting/ae967ece-bc34-426f-97f7-b28f7eae801e/page/p_yv5ggm2yrc"

def format_dashboard_data_as_text(dashboard_data):
    """Format extracted data as readable text"""
    lines = []

    # Add metadata
    metadata = dashboard_data.get('metadata', {})
    lines.append("=" * 80)
    lines.append("DASHBOARD EXTRACTION TEST RESULTS")
    lines.append("=" * 80)
    if metadata.get('dashboard_title'):
        lines.append(f"Dashboard: {metadata['dashboard_title']}")
    lines.append(f"URL: {metadata.get('url', 'N/A')}")
    lines.append(f"Extracted: {metadata.get('timestamp', 'N/A')}")
    lines.append("")

    # Add metrics/KPIs
    metrics = dashboard_data.get('metrics', [])
    if metrics:
        lines.append("=" * 80)
        lines.append("KEY METRICS & KPIs")
        lines.append("=" * 80)
        for idx, metric in enumerate(metrics[:20], 1):  # Limit to first 20
            if metric.get('metric_name'):
                lines.append(f"{idx}. {metric['metric_name']}: {metric.get('metric_value', 'N/A')}")
            else:
                lines.append(f"{idx}. {metric.get('metric_value', 'N/A')}")
        if len(metrics) > 20:
            lines.append(f"... and {len(metrics) - 20} more metrics")
        lines.append("")

    # Add tables
    tables = dashboard_data.get('tables', [])
    if tables:
        lines.append("=" * 80)
        lines.append("DATA TABLES")
        lines.append("=" * 80)
        for table in tables:
            lines.append(f"\n{table.get('table_id', 'Table')} ({table.get('row_count', 0)} rows, {table.get('column_count', 0)} columns):")

            # Add headers
            if table.get('headers'):
                lines.append("Headers: " + " | ".join(table['headers']))
                lines.append("-" * 80)

            # Add first 5 rows
            for row in table.get('rows', [])[:5]:
                lines.append(" | ".join(str(cell) for cell in row))

            if table.get('row_count', 0) > 5:
                lines.append(f"... ({table['row_count'] - 5} more rows)")
            lines.append("")

    # Add OCR extracted text
    ocr_data = dashboard_data.get('ocr_text', [])
    if ocr_data:
        lines.append("=" * 80)
        lines.append("OCR EXTRACTED TEXT (from images/canvas)")
        lines.append("=" * 80)
        for idx, ocr_item in enumerate(ocr_data, 1):
            source = ocr_item.get('source', f'extraction_{idx}')
            text = ocr_item.get('text', '')
            char_count = ocr_item.get('char_count', 0)
            if text:
                lines.append(f"\n[{source}] ({char_count} characters):")
                lines.append("-" * 80)
                lines.append(text)
                lines.append("")

    # Add navigation info
    navigation = dashboard_data.get('navigation_explored', [])
    if navigation:
        lines.append("=" * 80)
        lines.append("EXPLORED TABS/PAGES")
        lines.append("=" * 80)
        lines.append(f"Navigated through {len(navigation)} tabs: {', '.join(navigation)}")
        lines.append("")

    # Add summary
    summary = dashboard_data.get('summary', {})
    lines.append("=" * 80)
    lines.append("EXTRACTION SUMMARY")
    lines.append("=" * 80)
    lines.append(f"Total tables: {summary.get('total_tables', 0)}")
    lines.append(f"Total metrics: {summary.get('total_metrics', 0)}")
    lines.append(f"Total charts: {summary.get('total_charts', 0)}")
    lines.append(f"Total filters: {summary.get('total_filters', 0)}")
    if summary.get('total_ocr_extractions'):
        lines.append(f"Total OCR extractions: {summary.get('total_ocr_extractions', 0)} ({summary.get('total_ocr_characters', 0)} characters)")

    return "\n".join(lines)

def main():
    print("=" * 80)
    print("DASHBOARD SCRAPER TEST")
    print("=" * 80)
    print(f"Testing URL: {DASHBOARD_URL}")
    print()

    try:
        # Use headless mode for testing
        with sync_playwright() as p:
            print("🌐 Launching browser...")
            browser = p.chromium.launch(
                headless=False,  # Set to True for headless mode
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )

            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            page = context.new_page()

            # Remove webdriver property
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            print("📄 Navigating to dashboard...")
            page.goto(DASHBOARD_URL, wait_until='load', timeout=60000)

            print(f"✓ Page loaded: {page.title()}")

            # Wait a bit for initial content
            time.sleep(5)

            # Create extractor
            print("\n📊 Creating extractor...")
            extractor = LookerStudioExtractor(page)

            # Extract all data with navigation exploration and OCR
            print("\n🔍 Starting extraction (with OCR enabled)...\n")
            dashboard_data = extractor.extract_all_data(
                explore_nav=True,  # Enable navigation exploration
                enable_scrolling=True,  # Enable full scrolling
                enable_ocr=True  # Enable OCR to extract text from images/canvas
            )

            # Format results
            print("\n" + "=" * 80)
            print("EXTRACTION COMPLETE!")
            print("=" * 80)
            results_text = format_dashboard_data_as_text(dashboard_data)
            print(results_text)

            # Save results to file
            output_file = 'scraper_test_results.txt'
            with open(output_file, 'w') as f:
                f.write(results_text)

            print(f"\n✓ Results saved to: {output_file}")

            # Also save raw JSON
            json_file = 'scraper_test_results.json'
            with open(json_file, 'w') as f:
                json.dump(dashboard_data, f, indent=2)

            print(f"✓ Raw JSON saved to: {json_file}")

            # Close browser
            context.close()
            browser.close()

            print("\n✓ Test complete!")

    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
