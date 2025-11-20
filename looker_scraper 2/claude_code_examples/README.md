# Looker Studio Scraper - Authentication Bypass Implementation

This package contains complete, ready-to-use code for bypassing Google's authentication blocks when scraping Looker Studio dashboards using Playwright's persistent browser context method.

## Files Included

| File | Description |
|------|-------------|
| `authenticate.py` | One-time authentication script - run this first |
| `scrape_dashboard.py` | Standalone scraper script with data extraction |
| `flask_api_example.py` | Flask API integration example |
| `requirements.txt` | Python dependencies |
| `README.md` | This file |

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install
```

### 2. Authenticate (One-Time Setup)

Run the authentication script to log in manually and save your session:

```bash
python authenticate.py
```

**What happens:**
- A browser window will open
- Log in to your Google account
- Navigate to a Looker Studio dashboard to confirm login
- Close the browser window when done
- Your session is saved to `./my_google_session/`

### 3. Scrape Dashboards

Now you can scrape any dashboard without logging in again:

```bash
python scrape_dashboard.py
```

**Edit the script** to change the dashboard URL:
```python
dashboard_url = 'YOUR_LOOKER_STUDIO_URL_HERE'
```

## Integration Options

### Option A: Standalone Script

Use `scrape_dashboard.py` as-is for one-off scraping tasks. The script will:
- Load your saved session
- Navigate to the dashboard
- Extract all content
- Save a screenshot
- Export results to JSON

### Option B: Flask API

Use `flask_api_example.py` to create a REST API for your scraping needs:

```bash
python flask_api_example.py
```

Then make POST requests to scrape dashboards:

```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "YOUR_DASHBOARD_URL", "wait_time": 15}'
```

### Option C: Custom Integration

Import the scraping logic into your own Python application:

```python
from playwright.sync_api import sync_playwright

USER_DATA_DIR = './my_google_session'

def scrape_dashboard(url):
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(url)
        content = page.inner_text('body')
        context.close()
        return content
```

## How It Works

### The Problem
Google detects automated browsers and blocks login attempts with security warnings like "This app isn't verified" or "Sign in with Google temporarily disabled."

### The Solution
Instead of automating the login process, we use **persistent browser context**:

1. **Manual Login Once**: You log in manually in a real browser window
2. **Session Saved**: All cookies and authentication tokens are saved to a folder
3. **Reuse Session**: Future scraping uses this saved session, bypassing login entirely

This makes the automated browser appear identical to a regular browser session, completely avoiding Google's security checks.

## Key Features

✅ **No repeated logins** - Authenticate once, scrape forever (until session expires)  
✅ **Bypasses Google security** - Uses persistent context to appear as a real browser  
✅ **Session persistence** - Sessions typically last 30-90 days  
✅ **Headless operation** - Can run in background after initial authentication  
✅ **Screenshot capture** - Automatically saves dashboard screenshots  
✅ **Error handling** - Detects expired sessions and prompts re-authentication  

## Customizing Data Extraction

The `scrape_dashboard.py` script includes a basic extraction example. You can customize it to extract specific metrics:

```python
# Example: Extract specific metrics
metrics = {}
all_text = dashboard_content.split('\n')

for i, line in enumerate(all_text):
    if 'CPM' in line and i + 1 < len(all_text):
        metrics['CPM'] = all_text[i + 1]
    elif 'CPC' in line and i + 1 < len(all_text):
        metrics['CPC'] = all_text[i + 1]
    # Add more metrics as needed
```

For more advanced extraction, you can use Playwright's selectors to target specific elements:

```python
# Extract by CSS selector
cpm_value = page.locator('[data-metric="cpm"]').inner_text()

# Extract all table data
table_data = page.locator('table').all_inner_texts()
```

## Troubleshooting

### "Session has expired"

If you see this error, your Google session has expired (typically after 30-90 days). Simply run the authentication script again:

```bash
python authenticate.py
```

### "Target page, context or browser has been closed"

This usually means Playwright browsers aren't installed. Run:

```bash
playwright install
```

### Still getting blocked

If Google still blocks you:
1. Make sure you're using the same IP address for authentication and scraping
2. Add random delays between requests: `time.sleep(random.randint(5, 15))`
3. Use a more recent user agent string
4. Consider using a residential proxy

### Dashboard not loading completely

Increase the `wait_time` parameter:

```python
scrape_looker_studio(url, wait_time=30)  # Wait 30 seconds instead of 15
```

## Session Management

### Where is the session stored?

The session is saved in the `./my_google_session/` folder in your project directory. This folder contains:
- Cookies
- Local storage
- Session tokens
- Browser cache

### How long does the session last?

Google sessions typically last 30-90 days, depending on your account settings and Google's security policies.

### Can I use the same session on multiple machines?

No. The session is tied to the machine and IP address where it was created. You'll need to authenticate separately on each machine.

### Is my session secure?

The session folder contains your authentication tokens. Keep it secure:
- Don't commit it to version control (add to `.gitignore`)
- Don't share it with others
- Store it in a secure location
- Delete it when no longer needed

## Production Deployment

For production use, consider:

1. **Environment Variables**: Store the session directory path in an environment variable
2. **Session Refresh**: Implement automatic re-authentication when sessions expire
3. **Rate Limiting**: Add delays between requests to avoid triggering rate limits
4. **Error Logging**: Log all errors for debugging
5. **Monitoring**: Monitor session health and alert when re-authentication is needed

## Alternative: Direct API Access

If you have access to the underlying data sources (Google Ads, Facebook Ads, etc.), consider using their official APIs instead of scraping Looker Studio. This is more reliable and doesn't require any authentication workarounds.

See the main solution guide for more information on this approach.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the step-by-step guide in `claude_code_auth_bypass_guide.md`
3. Ensure you're using the latest version of Playwright

## License

This code is provided as-is for educational and personal use.
