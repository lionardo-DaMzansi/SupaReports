"""
Test script for the Looker Studio scraper
"""
import requests
import json
import sys


def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    try:
        response = requests.get('http://localhost:5000/health')
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_scrape(url):
    """Test the scraping endpoint with a URL"""
    print(f"\nTesting scrape endpoint with URL: {url}")
    try:
        response = requests.post(
            'http://localhost:5000/scrape',
            json={'url': url},
            timeout=120  # 2 minute timeout for scraping
        )
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        
        # Pretty print the response
        print("\n" + "="*80)
        print("SCRAPING RESULTS")
        print("="*80)
        print(json.dumps(data, indent=2))
        print("="*80)
        
        # Print summary if available
        if 'summary' in data:
            print("\nSUMMARY:")
            print(f"  Tables: {data['summary'].get('total_tables', 0)}")
            print(f"  Metrics: {data['summary'].get('total_metrics', 0)}")
            print(f"  Charts: {data['summary'].get('total_charts', 0)}")
            print(f"  Filters: {data['summary'].get('total_filters', 0)}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Main test function"""
    print("="*80)
    print("LOOKER STUDIO SCRAPER TEST SUITE")
    print("="*80)
    
    # Test health check
    health_ok = test_health_check()
    
    if not health_ok:
        print("\n❌ Health check failed. Make sure the server is running:")
        print("   python3 app_v2.py")
        sys.exit(1)
    
    print("\n✅ Health check passed!")
    
    # Test scraping with URL from command line
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        scrape_ok = test_scrape(test_url)
        
        if scrape_ok:
            print("\n✅ Scraping test passed!")
        else:
            print("\n❌ Scraping test failed!")
            sys.exit(1)
    else:
        print("\nTo test scraping, run:")
        print("  python3 test_scraper.py <your_looker_studio_url>")
        print("\nExample:")
        print("  python3 test_scraper.py https://lookerstudio.google.com/reporting/...")


if __name__ == '__main__':
    main()
