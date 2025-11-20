from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import time
import json

app = Flask(__name__)

def scrape_looker_dashboard(url):
    """
    Scrape a Looker Studio dashboard and extract all data including tables, charts, and metrics.
    
    Args:
        url (str): The Looker Studio dashboard URL
        
    Returns:
        dict: Extracted data in JSON format
    """
    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        try:
            # Navigate to the dashboard
            print(f"Navigating to: {url}")
            page.goto(url, wait_until='networkidle', timeout=60000)
            
            # Wait for dashboard to load
            time.sleep(5)
            
            # Initialize data structure
            dashboard_data = {
                'url': url,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'tables': [],
                'metrics': [],
                'charts': [],
                'text_elements': []
            }
            
            # Extract all tables
            tables = page.query_selector_all('table')
            for idx, table in enumerate(tables):
                try:
                    rows = table.query_selector_all('tr')
                    table_data = []
                    for row in rows:
                        cells = row.query_selector_all('td, th')
                        row_data = [cell.inner_text().strip() for cell in cells]
                        if row_data:  # Only add non-empty rows
                            table_data.append(row_data)
                    
                    if table_data:
                        dashboard_data['tables'].append({
                            'table_id': f'table_{idx + 1}',
                            'data': table_data
                        })
                except Exception as e:
                    print(f"Error extracting table {idx}: {e}")
            
            # Extract metric cards/scorecard elements
            # Looker Studio often uses specific classes for metrics
            metric_selectors = [
                '[class*="scorecard"]',
                '[class*="metric"]',
                '[class*="kpi"]',
                '[data-test-id*="scorecard"]'
            ]
            
            for selector in metric_selectors:
                elements = page.query_selector_all(selector)
                for idx, element in enumerate(elements):
                    try:
                        text = element.inner_text().strip()
                        if text and text not in [m['value'] for m in dashboard_data['metrics']]:
                            dashboard_data['metrics'].append({
                                'metric_id': f'metric_{len(dashboard_data["metrics"]) + 1}',
                                'value': text
                            })
                    except Exception as e:
                        print(f"Error extracting metric: {e}")
            
            # Extract chart data (canvas elements, SVG, etc.)
            charts = page.query_selector_all('canvas, svg[class*="chart"]')
            for idx, chart in enumerate(charts):
                try:
                    # Get chart container for context
                    parent = chart.evaluate('el => el.parentElement')
                    chart_info = {
                        'chart_id': f'chart_{idx + 1}',
                        'type': chart.evaluate('el => el.tagName'),
                    }
                    
                    # Try to extract any visible text near the chart (labels, legends)
                    if parent:
                        nearby_text = page.evaluate(
                            '(el) => el.innerText',
                            chart.evaluate('el => el.parentElement')
                        )
                        if nearby_text:
                            chart_info['labels'] = nearby_text.strip()
                    
                    dashboard_data['charts'].append(chart_info)
                except Exception as e:
                    print(f"Error extracting chart {idx}: {e}")
            
            # Extract all text elements that might contain data
            text_elements = page.query_selector_all('div[class*="text"], span[class*="label"], p')
            seen_texts = set()
            for element in text_elements:
                try:
                    text = element.inner_text().strip()
                    # Filter out empty, duplicate, or very long texts
                    if text and len(text) < 500 and text not in seen_texts:
                        seen_texts.add(text)
                        dashboard_data['text_elements'].append(text)
                except Exception as e:
                    continue
            
            # Try to find and click through any navigation elements (tabs, buttons, pages)
            navigation_elements = page.query_selector_all(
                'button, [role="tab"], [class*="tab"], [class*="page"], [class*="navigation"]'
            )
            
            clicked_elements = []
            for idx, nav_element in enumerate(navigation_elements[:10]):  # Limit to first 10 to avoid infinite loops
                try:
                    # Check if element is visible and clickable
                    if nav_element.is_visible():
                        element_text = nav_element.inner_text().strip()
                        print(f"Clicking navigation element: {element_text}")
                        
                        nav_element.click()
                        time.sleep(3)  # Wait for content to load
                        
                        # Extract additional data after navigation
                        new_tables = page.query_selector_all('table')
                        for t_idx, table in enumerate(new_tables):
                            try:
                                rows = table.query_selector_all('tr')
                                table_data = []
                                for row in rows:
                                    cells = row.query_selector_all('td, th')
                                    row_data = [cell.inner_text().strip() for cell in cells]
                                    if row_data:
                                        table_data.append(row_data)
                                
                                if table_data and table_data not in [t['data'] for t in dashboard_data['tables']]:
                                    dashboard_data['tables'].append({
                                        'table_id': f'table_nav_{idx}_{t_idx + 1}',
                                        'source': element_text,
                                        'data': table_data
                                    })
                            except Exception as e:
                                print(f"Error extracting navigated table: {e}")
                        
                        clicked_elements.append(element_text)
                except Exception as e:
                    print(f"Error clicking navigation element: {e}")
                    continue
            
            dashboard_data['navigation_explored'] = clicked_elements
            
            # Get page title
            dashboard_data['title'] = page.title()
            
            print(f"Extraction complete. Found {len(dashboard_data['tables'])} tables, "
                  f"{len(dashboard_data['metrics'])} metrics, {len(dashboard_data['charts'])} charts")
            
            return dashboard_data
            
        except Exception as e:
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
        "url": "https://lookerstudio.google.com/..."
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
                    'url': 'https://lookerstudio.google.com/reporting/...'
                }
            }), 400
        
        url = data['url']
        
        # Validate URL
        if not url.startswith('http'):
            return jsonify({
                'error': 'Invalid URL format. Must start with http:// or https://'
            }), 400
        
        # Scrape the dashboard
        result = scrape_looker_dashboard(url)
        
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
        'version': '1.0.0'
    }), 200


@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API documentation"""
    return jsonify({
        'service': 'Looker Studio Dashboard Scraper',
        'version': '1.0.0',
        'endpoints': {
            '/scrape': {
                'method': 'POST',
                'description': 'Scrape a Looker Studio dashboard',
                'payload': {
                    'url': 'https://lookerstudio.google.com/reporting/...'
                },
                'response': {
                    'url': 'string',
                    'timestamp': 'string',
                    'title': 'string',
                    'tables': 'array',
                    'metrics': 'array',
                    'charts': 'array',
                    'text_elements': 'array',
                    'navigation_explored': 'array'
                }
            },
            '/health': {
                'method': 'GET',
                'description': 'Health check endpoint'
            }
        },
        'usage_example': {
            'curl': 'curl -X POST http://localhost:5000/scrape -H "Content-Type: application/json" -d \'{"url": "https://lookerstudio.google.com/reporting/YOUR_DASHBOARD_ID"}\''
        }
    }), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
