# Looker Studio Dashboard Scraper

A Flask-based API service that uses Playwright to scrape Looker Studio dashboards and extract paid media metrics, tables, charts, and other data as JSON.

## Features

- **Automatic Navigation**: Clicks through tabs, pages, and navigation elements to discover all dashboard data
- **Comprehensive Data Extraction**: Extracts tables, metrics, charts, filters, and text elements
- **JSON API**: Returns all data in a structured JSON format for easy integration
- **Headless Browser**: Runs without opening visible browser windows
- **No Authentication Required**: Works with publicly accessible Looker Studio dashboards

## What Gets Extracted

- **Tables**: All data tables with headers and rows
- **Metrics/KPIs**: Scorecard values and key performance indicators
- **Charts**: Chart information including titles and labels
- **Filters**: Active filter values
- **Metadata**: Dashboard title, URL, timestamp
- **Navigation**: Automatically explores tabs and pages

## Installation

### Prerequisites

- Python 3.7 or higher
- pip3

### Quick Setup

1. **Run the setup script**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

### Manual Setup

1. **Install Python dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Install Playwright browsers**:
   ```bash
   python3 -m playwright install chromium
   ```

## Usage

### Starting the Server

```bash
python3 app_v2.py
```

The API will be available at `http://localhost:5000`

### API Endpoints

#### 1. Health Check
```bash
GET http://localhost:5000/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "Looker Studio Scraper",
  "version": "2.0.0"
}
```

#### 2. Scrape Dashboard
```bash
POST http://localhost:5000/scrape
Content-Type: application/json

{
  "url": "https://lookerstudio.google.com/reporting/YOUR_DASHBOARD_ID",
  "explore_navigation": true
}
```

**Parameters**:
- `url` (required): The Looker Studio dashboard URL
- `explore_navigation` (optional): Whether to click through navigation elements (default: true)

**Response**:
```json
{
  "metadata": {
    "title": "Dashboard Title",
    "url": "https://lookerstudio.google.com/...",
    "timestamp": "2025-11-08 12:00:00",
    "dashboard_title": "Paid Media Performance"
  },
  "tables": [
    {
      "table_id": "table_1",
      "headers": ["Campaign", "Impressions", "Clicks", "Cost"],
      "rows": [
        ["Campaign A", "10,000", "500", "$250"],
        ["Campaign B", "8,000", "400", "$200"]
      ],
      "row_count": 2,
      "column_count": 4
    }
  ],
  "metrics": [
    {
      "metric_name": "Total Impressions",
      "metric_value": "18,000",
      "full_text": "Total Impressions\n18,000"
    }
  ],
  "charts": [
    {
      "chart_id": "chart_1",
      "type": "CANVAS",
      "title": "Impressions Over Time",
      "labels": ["Jan", "Feb", "Mar"]
    }
  ],
  "filters": [
    {
      "name": "Date Range",
      "value": "Last 30 days"
    }
  ],
  "navigation_explored": ["Overview", "Campaigns", "Performance"],
  "summary": {
    "total_tables": 1,
    "total_metrics": 1,
    "total_charts": 1,
    "total_filters": 1
  }
}
```

### Integration Examples

#### Python
```python
import requests

response = requests.post(
    'http://localhost:5000/scrape',
    json={
        'url': 'https://lookerstudio.google.com/reporting/YOUR_DASHBOARD_ID'
    }
)

data = response.json()

# Access tables
for table in data['tables']:
    print(f"Table: {table['table_id']}")
    print(f"Headers: {table['headers']}")
    for row in table['rows']:
        print(row)

# Access metrics
for metric in data['metrics']:
    print(f"{metric['metric_name']}: {metric['metric_value']}")
```

#### cURL
```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://lookerstudio.google.com/reporting/YOUR_DASHBOARD_ID"
  }'
```

#### JavaScript/Node.js
```javascript
fetch('http://localhost:5000/scrape', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        url: 'https://lookerstudio.google.com/reporting/YOUR_DASHBOARD_ID'
    })
})
.then(response => response.json())
.then(data => {
    console.log('Tables:', data.tables);
    console.log('Metrics:', data.metrics);
    console.log('Summary:', data.summary);
});
```

#### From Your Flask App
```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/get-dashboard-data', methods=['POST'])
def get_dashboard_data():
    # Get dashboard URL from your app's request
    dashboard_url = request.json.get('dashboard_url')
    
    # Call the scraper API
    response = requests.post(
        'http://localhost:5000/scrape',
        json={'url': dashboard_url}
    )
    
    # Return the scraped data to your app
    return jsonify(response.json())
```

## Testing

### Test the Health Endpoint
```bash
python3 test_scraper.py
```

### Test with a Real Dashboard
```bash
python3 test_scraper.py https://lookerstudio.google.com/reporting/YOUR_DASHBOARD_ID
```

## File Structure

```
looker_scraper/
├── app_v2.py              # Main Flask application (recommended)
├── app.py                 # Alternative simpler version
├── looker_extractor.py    # Enhanced data extraction logic
├── requirements.txt       # Python dependencies
├── setup.sh              # Installation script
├── test_scraper.py       # Test suite
└── README.md             # This file
```

## Configuration

### Change Port
Edit `app_v2.py` and modify the last line:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change 5000 to your port
```

### Disable Navigation Exploration
Send `explore_navigation: false` in your request:
```json
{
  "url": "https://lookerstudio.google.com/...",
  "explore_navigation": false
}
```

### Adjust Timeouts
Edit `looker_extractor.py` and modify the `wait_for_dashboard_load` method:
```python
def wait_for_dashboard_load(self, timeout=10):  # Change timeout value
```

## Troubleshooting

### Server Won't Start
- Make sure port 5000 is not in use
- Check that all dependencies are installed: `pip3 install -r requirements.txt`
- Verify Playwright browsers are installed: `python3 -m playwright install chromium`

### No Data Extracted
- Verify the dashboard URL is publicly accessible
- Try disabling navigation exploration: `"explore_navigation": false`
- Check if the dashboard requires authentication (not currently supported)
- Increase wait timeouts in `looker_extractor.py`

### Timeout Errors
- Increase the timeout in the scrape request
- Check your internet connection
- Verify the Looker Studio dashboard loads properly in a regular browser

### Empty Tables/Metrics
- Looker Studio dashboards use dynamic loading - try increasing wait times
- Some dashboards may use custom elements not covered by default selectors
- Check the browser console for JavaScript errors

## Performance

- **Average scraping time**: 10-30 seconds per dashboard
- **Memory usage**: ~200-500 MB per request
- **Concurrent requests**: Supports multiple simultaneous scraping requests

## Limitations

- Only works with publicly accessible Looker Studio dashboards
- Cannot handle dashboards requiring Google authentication
- May not extract all data from highly customized dashboards
- Performance depends on dashboard complexity and size

## Security Notes

- This tool is designed for scraping publicly accessible dashboards
- Do not use for scraping private or authenticated dashboards without permission
- Respect Looker Studio's terms of service
- Rate limit your requests to avoid overloading the service

## License

This project is provided as-is for educational and development purposes.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the test output for error messages
3. Verify your dashboard URL is publicly accessible
4. Check Playwright and Flask logs for detailed error information

## Version History

- **v2.0.0**: Enhanced extraction with dedicated Looker Studio extractor class
- **v1.0.0**: Initial release with basic scraping functionality
