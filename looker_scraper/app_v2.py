from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
from looker_extractor import LookerStudioExtractor
import time

app = Flask(__name__)


def scrape_looker_dashboard(url, explore_navigation=True):
    """
    Scrape a Looker Studio dashboard and extract all data.
    
    Args:
        url (str): The Looker Studio dashboard URL
        explore_navigation (bool): Whether to click through navigation elements
        
    Returns:
        dict: Extracted data in JSON format
    """
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        try:
            print(f"Navigating to: {url}")
            
            # Navigate to the dashboard
            page.goto(url, wait_until='networkidle', timeout=60000)
            
            # Create extractor instance
            extractor = LookerStudioExtractor(page)
            
            # Extract all data
            dashboard_data = extractor.extract_all_data(explore_nav=explore_navigation)
            
            return dashboard_data
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            return {
                'error': str(e),
                'url': url,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        finally:
            browser.close()


@app.route('/scrape', methods=['POST'])
def scrape_endpoint():
    """
    API endpoint to scrape a Looker Studio dashboard.
    
    Expected JSON payload:
    {
        "url": "https://lookerstudio.google.com/...",
        "explore_navigation": true  // optional, default: true
    }
    
    Returns:
        JSON response with extracted data
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'error': 'Missing required parameter: url',
                'example': {
                    'url': 'https://lookerstudio.google.com/reporting/...',
                    'explore_navigation': True
                }
            }), 400
        
        url = data['url']
        explore_navigation = data.get('explore_navigation', True)
        
        # Validate URL
        if not url.startswith('http'):
            return jsonify({
                'error': 'Invalid URL format. Must start with http:// or https://'
            }), 400
        
        print(f"Received scraping request for: {url}")
        
        # Scrape the dashboard
        result = scrape_looker_dashboard(url, explore_navigation)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Looker Studio Scraper',
        'version': '2.0.0'
    }), 200


@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API documentation"""
    return jsonify({
        'service': 'Looker Studio Dashboard Scraper',
        'version': '2.0.0',
        'description': 'Extract paid media metrics, tables, charts, and data from Looker Studio dashboards',
        'endpoints': {
            '/scrape': {
                'method': 'POST',
                'description': 'Scrape a Looker Studio dashboard and return all data as JSON',
                'payload': {
                    'url': 'https://lookerstudio.google.com/reporting/YOUR_DASHBOARD_ID',
                    'explore_navigation': True  # Optional: click through tabs/pages
                },
                'response': {
                    'metadata': {
                        'title': 'Page title',
                        'url': 'Dashboard URL',
                        'timestamp': 'Extraction timestamp',
                        'dashboard_title': 'Dashboard title from page'
                    },
                    'tables': [
                        {
                            'table_id': 'Unique table identifier',
                            'headers': ['Column headers'],
                            'rows': [['Row data']],
                            'row_count': 'Number of rows',
                            'column_count': 'Number of columns'
                        }
                    ],
                    'metrics': [
                        {
                            'metric_name': 'Metric name',
                            'metric_value': 'Metric value',
                            'full_text': 'Complete text'
                        }
                    ],
                    'charts': [
                        {
                            'chart_id': 'Unique chart identifier',
                            'type': 'Chart element type',
                            'title': 'Chart title',
                            'labels': ['Chart labels']
                        }
                    ],
                    'filters': [
                        {
                            'name': 'Filter name',
                            'value': 'Current filter value'
                        }
                    ],
                    'navigation_explored': ['List of navigation elements clicked'],
                    'summary': {
                        'total_tables': 'Number of tables',
                        'total_metrics': 'Number of metrics',
                        'total_charts': 'Number of charts',
                        'total_filters': 'Number of filters'
                    }
                }
            },
            '/health': {
                'method': 'GET',
                'description': 'Health check endpoint'
            }
        },
        'usage_examples': {
            'curl': 'curl -X POST http://localhost:5000/scrape -H "Content-Type: application/json" -d \'{"url": "https://lookerstudio.google.com/reporting/YOUR_DASHBOARD_ID"}\'',
            'python': '''
import requests

response = requests.post(
    'http://localhost:5000/scrape',
    json={'url': 'https://lookerstudio.google.com/reporting/YOUR_DASHBOARD_ID'}
)

data = response.json()
print(data)
            ''',
            'javascript': '''
fetch('http://localhost:5000/scrape', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        url: 'https://lookerstudio.google.com/reporting/YOUR_DASHBOARD_ID'
    })
})
.then(response => response.json())
.then(data => console.log(data));
            '''
        }
    }), 200


if __name__ == '__main__':
    print("Starting Looker Studio Scraper API...")
    print("API will be available at http://localhost:5000")
    print("Visit http://localhost:5000 for API documentation")
    app.run(debug=True, host='0.0.0.0', port=5000)
