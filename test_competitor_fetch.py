#!/usr/bin/env python3
"""
Test script for competitor URL fetching functionality
"""
import sys
import os

# Add current directory to path so we can import from app.py
sys.path.insert(0, os.path.dirname(__file__))

from app import fetch_url_content, fetch_competitor_insights

# Test URLs
test_urls = [
    "https://www.mtn.co.za/",
    "https://www.vodacom.co.za/"
]

def main():
    print("=" * 80)
    print("COMPETITOR URL FETCH TEST")
    print("=" * 80)
    print()

    # Test 1: Single URL fetch
    print("TEST 1: Fetching single URL")
    print("-" * 80)
    result = fetch_url_content(test_urls[0])

    if result['success']:
        print(f"✓ Success!")
        print(f"  Title: {result['title']}")
        print(f"  URL: {result['url']}")
        print(f"  Text length: {len(result['text'])} characters")
        print(f"  First 200 chars: {result['text'][:200]}...")
    else:
        print(f"✗ Failed: {result['error']}")

    print()

    # Test 2: Multiple URLs with formatting
    print("TEST 2: Fetching multiple URLs with formatting")
    print("-" * 80)
    insights = fetch_competitor_insights(test_urls)

    if insights:
        print("✓ Formatted insights generated!")
        print()
        print("First 500 characters of formatted output:")
        print("-" * 80)
        print(insights[:500])
        print("...")
        print()
        print(f"Total insights length: {len(insights)} characters")
    else:
        print("✗ No insights generated")

    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
