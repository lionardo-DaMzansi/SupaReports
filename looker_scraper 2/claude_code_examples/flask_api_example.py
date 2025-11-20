#!/usr/bin/env python3
"""
Flask API for Looker Studio Scraping
Integrates the authentication bypass method into a Flask application.
"""
from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import time
import os

app = Flask(__name__)

# Persistent browser profile directory
USER_DATA_DIR = './my_google_session'


def scrape_with_saved_session(url: str, wait_time: int = 15):
    """
    Scrape a Looker Studio dashboard using saved authentication session.
    
    Args:
        url: Dashboard URL
        wait_time: Time to wait for dashboard to load
    
    Returns:
        Dictionary with scraped data or error
    """
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
            ]
        )
        
        page = context.pages[0] if context.pages else context.new_page()
        
        try:
            page.goto(url, wait_until='networkidle', timeout=90000)
            
            # Check if login required
            if 'accounts.google.com' in page.url:
                context.close()
                return {
                    'status': 'error',
                    'error': 'Authentication required. Session may have expired.',
                    'message': 'Please re-authenticate by running authenticate.py'
                }
            
            # Wait for dashboard to load
            time.sleep(wait_time)
            
            # Extract data
            content = page.inner_text('body')
            title = page.title()
            
            # Take screenshot
            screenshot_path = f'screenshots/dashboard_{int(time.time())}.png'
            os.makedirs('screenshots', exist_ok=True)
            page.screenshot(path=screenshot_path, full_page=True)
            
            context.close()
            
            return {
                'status': 'success',
                'title': title,
                'url': page.url,
                'content': content,
                'content_length': len(content),
                'screenshot': screenshot_path,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            context.close()
            return {
                'status': 'error',
                'error': str(e)
            }


@app.route('/', methods=['GET'])
def home():
    """API documentation."""
    return jsonify({
        'service': 'Looker Studio Scraper API',
        'version': '1.0.0',
        'endpoints': {
            '/scrape': {
                'method': 'POST',
                'description': 'Scrape a Looker Studio dashboard',
                'payload': {
                    'url': 'Dashboard URL (required)',
                    'wait_time': 'Wait time in seconds (optional, default: 15)'
                },
                'example': {
                    'url': 'https://lookerstudio.google.com/reporting/...',
                    'wait_time': 15
                }
            },
            '/status': {
                'method': 'GET',
                'description': 'Check authentication status'
            }
        }
    }), 200


@app.route('/status', methods=['GET'])
def status():
    """Check authentication status."""
    session_exists = os.path.exists(USER_DATA_DIR) and os.listdir(USER_DATA_DIR)
    
    return jsonify({
        'authenticated': session_exists,
        'session_directory': USER_DATA_DIR,
        'message': 'Session active' if session_exists else 'No saved session. Please authenticate first.'
    }), 200


@app.route('/scrape', methods=['POST'])
def scrape():
    """
    Scrape a Looker Studio dashboard.
    
    Expected JSON payload:
    {
        "url": "https://lookerstudio.google.com/...",
        "wait_time": 15  // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'status': 'error',
                'error': 'Missing required parameter: url'
            }), 400
        
        url = data['url']
        wait_time = data.get('wait_time', 15)
        
        # Validate wait_time
        if not isinstance(wait_time, int) or wait_time < 1 or wait_time > 60:
            return jsonify({
                'status': 'error',
                'error': 'wait_time must be an integer between 1 and 60'
            }), 400
        
        print(f"Scraping: {url}")
        result = scrape_with_saved_session(url, wait_time)
        
        if result['status'] == 'error':
            return jsonify(result), 500
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Looker Studio Scraper API'
    }), 200


if __name__ == '__main__':
    print("=" * 80)
    print("Looker Studio Scraper API")
    print("=" * 80)
    print("Starting server on http://localhost:5000")
    print("\nMake sure you have authenticated first by running:")
    print("  python authenticate.py")
    print("\nThen you can scrape dashboards by sending POST requests to:")
    print("  http://localhost:5000/scrape")
    print("=" * 80)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
