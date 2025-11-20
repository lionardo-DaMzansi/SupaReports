#!/usr/bin/env python3
"""
Test research URLs functionality - enriching campaign analysis with best practices
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import fetch_competitor_insights

# Research URLs focused on best practices and industry insights
research_urls = [
    # YouTube best practices
    "https://blog.hootsuite.com/youtube-marketing/",

    # Social media benchmarks
    "https://www.wordstream.com/blog/ws/2023/11/07/facebook-ad-benchmarks",

    # Digital marketing trends
    "https://www.hubspot.com/marketing-statistics",

    # Video marketing best practices
    "https://sproutsocial.com/insights/video-marketing-statistics/"
]

def main():
    print("=" * 80)
    print("RESEARCH URLs TEST - Best Practice Enrichment")
    print("=" * 80)
    print()
    print("PURPOSE: Test fetching research URLs to enrich campaign insights")
    print("         with industry best practices, benchmarks, and trends")
    print()
    print(f"Testing {len(research_urls)} research URLs:")
    for idx, url in enumerate(research_urls, 1):
        print(f"  {idx}. {url}")
    print()
    print("=" * 80)
    print()

    # Fetch research insights
    print("🔍 Fetching research insights...")
    print()

    insights = fetch_competitor_insights(research_urls)

    if insights:
        print("\n" + "=" * 80)
        print("RESEARCH INSIGHTS EXTRACTED (First 2000 chars)")
        print("=" * 80)
        print()
        print(insights[:2000])
        print("\n... (truncated for display)")
        print()
        print("=" * 80)
        print(f"✓ Total insights length: {len(insights):,} characters")
        print("=" * 80)
        print()

        # Show what type of content was extracted
        print("CONTENT ANALYSIS:")
        print("-" * 80)
        if "YouTube" in insights or "youtube" in insights:
            print("✓ Contains YouTube best practices")
        if "benchmark" in insights.lower():
            print("✓ Contains benchmarking data")
        if "CTR" in insights or "click-through" in insights.lower():
            print("✓ Contains CTR metrics/best practices")
        if "video" in insights.lower():
            print("✓ Contains video marketing insights")
        if "engagement" in insights.lower():
            print("✓ Contains engagement best practices")

        print()
        print("=" * 80)
        print("USE CASE: This data enriches AI analysis with:")
        print("  • Industry benchmarks for campaign performance")
        print("  • Best practice recommendations for platforms")
        print("  • Trend insights for strategic recommendations")
        print("  • Contextual data to interpret client metrics")
        print("=" * 80)

    else:
        print("✗ No research insights generated")

    # Save to file
    output_file = "research_insights_test.txt"
    with open(output_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("RESEARCH URLs TEST RESULTS\n")
        f.write("=" * 80 + "\n\n")
        f.write("Research URLs tested:\n")
        for idx, url in enumerate(research_urls, 1):
            f.write(f"{idx}. {url}\n")
        f.write("\n" + "=" * 80 + "\n\n")
        f.write(insights)

    print(f"\n✓ Full insights saved to: {output_file}")
    print()

if __name__ == "__main__":
    main()
