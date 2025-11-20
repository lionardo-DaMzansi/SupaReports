"""
Example: How to integrate the Looker Studio scraper into your existing Flask app
"""
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# URL of the scraper API (running separately)
SCRAPER_API_URL = 'http://localhost:5000/scrape'


@app.route('/api/scrape-dashboard', methods=['POST'])
def scrape_dashboard():
    """
    Your app's endpoint that calls the scraper service
    
    Expected request:
    POST /api/scrape-dashboard
    {
        "dashboard_url": "https://lookerstudio.google.com/..."
    }
    """
    try:
        # Get the dashboard URL from your app's request
        data = request.get_json()
        dashboard_url = data.get('dashboard_url')
        
        if not dashboard_url:
            return jsonify({'error': 'dashboard_url is required'}), 400
        
        # Call the scraper API
        print(f"Scraping dashboard: {dashboard_url}")
        
        response = requests.post(
            SCRAPER_API_URL,
            json={
                'url': dashboard_url,
                'explore_navigation': True
            },
            timeout=120  # 2 minute timeout
        )
        
        # Check if scraping was successful
        if response.status_code != 200:
            return jsonify({
                'error': 'Scraping failed',
                'details': response.json()
            }), response.status_code
        
        # Get the scraped data
        scraped_data = response.json()
        
        # Process the data as needed for your app
        processed_data = process_dashboard_data(scraped_data)
        
        return jsonify(processed_data), 200
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Scraping timeout - dashboard took too long to load'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Cannot connect to scraper service. Is it running?'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def process_dashboard_data(scraped_data):
    """
    Process the scraped data for your specific needs
    
    This is where you can transform the raw scraped data into
    the format your app needs
    """
    # Example: Extract only the metrics and tables
    processed = {
        'dashboard_title': scraped_data.get('metadata', {}).get('dashboard_title', 'Unknown'),
        'extracted_at': scraped_data.get('metadata', {}).get('timestamp'),
        'metrics': [],
        'tables': [],
        'summary': scraped_data.get('summary', {})
    }
    
    # Process metrics
    for metric in scraped_data.get('metrics', []):
        processed['metrics'].append({
            'name': metric.get('metric_name', 'Unknown'),
            'value': metric.get('metric_value', 'N/A')
        })
    
    # Process tables
    for table in scraped_data.get('tables', []):
        processed['tables'].append({
            'id': table.get('table_id'),
            'headers': table.get('headers', []),
            'data': table.get('rows', []),
            'row_count': table.get('row_count', 0)
        })
    
    return processed


@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """
    Example: Generate a report from multiple dashboards
    
    Expected request:
    POST /api/generate-report
    {
        "dashboard_urls": [
            "https://lookerstudio.google.com/...",
            "https://lookerstudio.google.com/..."
        ]
    }
    """
    try:
        data = request.get_json()
        dashboard_urls = data.get('dashboard_urls', [])
        
        if not dashboard_urls:
            return jsonify({'error': 'dashboard_urls is required'}), 400
        
        report_data = {
            'dashboards': [],
            'combined_metrics': [],
            'total_tables': 0
        }
        
        # Scrape each dashboard
        for url in dashboard_urls:
            print(f"Scraping: {url}")
            
            response = requests.post(
                SCRAPER_API_URL,
                json={'url': url},
                timeout=120
            )
            
            if response.status_code == 200:
                dashboard_data = response.json()
                
                report_data['dashboards'].append({
                    'url': url,
                    'title': dashboard_data.get('metadata', {}).get('dashboard_title'),
                    'metrics_count': len(dashboard_data.get('metrics', [])),
                    'tables_count': len(dashboard_data.get('tables', []))
                })
                
                # Combine metrics
                report_data['combined_metrics'].extend(
                    dashboard_data.get('metrics', [])
                )
                
                report_data['total_tables'] += len(dashboard_data.get('tables', []))
        
        return jsonify(report_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check for your app"""
    # Also check if the scraper service is running
    try:
        scraper_health = requests.get('http://localhost:5000/health', timeout=5)
        scraper_status = 'healthy' if scraper_health.status_code == 200 else 'unhealthy'
    except:
        scraper_status = 'offline'
    
    return jsonify({
        'app_status': 'healthy',
        'scraper_service': scraper_status
    }), 200


if __name__ == '__main__':
    print("Starting your Flask app...")
    print("Make sure the scraper service is running on port 5000:")
    print("  python3 app_v2.py")
    print("")
    print("Your app will be available at http://localhost:8000")
    app.run(debug=True, host='0.0.0.0', port=8000)
