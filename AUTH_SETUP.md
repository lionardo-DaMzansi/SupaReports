# Google Authentication Setup for Looker Studio Dashboards

## Overview

Supa Reports can automatically scrape data from your Looker Studio dashboards, including **private/authenticated dashboards** that require Google login.

## How It Works

The scraper uses **persistent browser context** which allows you to:
1. Log in to Google **once** using a visible browser window
2. Your login session is saved locally in `browser_data/`
3. All future dashboard scraping uses your authenticated session automatically
4. No need to log in again (unless you clear the browser data)

## One-Time Setup (For Private Dashboards)

If your Looker Studio dashboards require Google authentication, run this setup once:

### Step 1: Run the Authentication Setup Script

```bash
python3 setup_google_auth.py
```

### Step 2: Log In When Browser Opens

1. A Chrome browser window will open
2. Log in to your Google account (the one with Looker Studio access)
3. Navigate to https://lookerstudio.google.com
4. Open one of your dashboards to verify you can access it
5. Return to the terminal and press Enter

### Step 3: Done!

Your authentication session is now saved. Future dashboard scraping will automatically use your logged-in session.

## Using Dashboard Links in Supa Reports

After authentication setup (or for public dashboards), simply:

1. Open Supa Reports at http://localhost:5173
2. Fill out the briefing form
3. In the "Dashboard Links" field, paste your Looker Studio URL(s)
   - Example: `https://lookerstudio.google.com/reporting/abc123...`
   - Multiple URLs: Separate with commas
4. Submit the form
5. The scraper will extract all tables, metrics, and charts automatically

## Troubleshooting

### "Dashboard requires authentication" Error

**Solution:** Run `python3 setup_google_auth.py` to log in

### Authentication Expired

If you get login errors after some time:

1. Delete the browser data: `rm -rf browser_data/`
2. Re-run the setup: `python3 setup_google_auth.py`

### Browser Won't Open

Check that Playwright's Chromium is installed:

```bash
python3 -m playwright install chromium
```

### Can't Access Dashboard After Login

Make sure you:
1. Use the correct Google account (one with dashboard access)
2. Actually navigate to and open a dashboard during setup
3. Wait for the dashboard to fully load before pressing Enter

## Security Notes

- The `browser_data/` directory contains your Google session cookies
- This directory is automatically excluded from git (in `.gitignore`)
- Keep this directory secure - it grants access to your Google account
- Only run the setup script on your personal/trusted machine
- To revoke access: Delete the `browser_data/` directory

## Public Dashboards

For **public** Looker Studio dashboards (no login required):
- No authentication setup needed
- Just paste the URL in the Dashboard Links field
- Scraping works immediately

## What Gets Extracted

From each dashboard, the scraper extracts:

- ✅ **Tables**: All data tables with headers and rows
- ✅ **Metrics/KPIs**: Scorecard values (impressions, clicks, etc.)
- ✅ **Charts**: Chart information and labels
- ✅ **Filters**: Active filter values
- ✅ **Navigation**: Clicks through tabs/pages automatically
- ✅ **Metadata**: Dashboard title, timestamp

All extracted data is formatted as text and passed to GPT-4 for analysis in your report.

## Support

If you encounter issues:

1. Check that the Flask server is running: `python3 app.py`
2. Verify Playwright is installed: `python3 -m playwright install chromium`
3. Try re-running authentication setup
4. Check server logs for detailed error messages
