#!/usr/bin/env python3
"""
Detailed test showing full competitor insights output
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import fetch_competitor_insights

# Test URLs - mix of competitor and research URLs
test_urls = [
    "https://www.mtn.co.za/",
    "https://www.vodacom.co.za/",
    "https://www.techcrunch.com/2024/01/15/ai-marketing-trends/"
]

def main():
    print("=" * 80)
    print("FULL COMPETITOR INSIGHTS TEST")
    print("=" * 80)
    print(f"Testing with {len(test_urls)} URLs")
    print()

    # Fetch and format insights
    insights = fetch_competitor_insights(test_urls)

    if insights:
        print("\n" + "=" * 80)
        print("COMPLETE FORMATTED OUTPUT (as sent to AI)")
        print("=" * 80)
        print()
        print(insights)
        print()
        print("=" * 80)
        print(f"Total length: {len(insights)} characters")
        print("=" * 80)
    else:
        print("✗ No insights generated")

if __name__ == "__main__":
    main()
