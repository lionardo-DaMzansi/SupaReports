# Quick Start Guide

Get the Looker Studio scraper running in 3 minutes!

## Step 1: Install Dependencies

```bash
cd looker_scraper
./setup.sh
```

Or manually:
```bash
pip3 install -r requirements.txt
python3 -m playwright install chromium
```

## Step 2: Start the Scraper API

```bash
python3 app_v2.py
```

You should see:
```
Starting Looker Studio Scraper API...
API will be available at http://localhost:5000
 * Running on http://0.0.0.0:5000
```

## Step 3: Test It

Open a new terminal and test the health endpoint:

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Looker Studio Scraper",
  "version": "2.0.0"
}
```

## Step 4: Scrape Your First Dashboard

Replace `YOUR_DASHBOARD_URL` with your actual Looker Studio dashboard URL:

```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "YOUR_DASHBOARD_URL"}'
```

Or use Python:

```python
import requests

response = requests.post(
    'http://localhost:5000/scrape',
    json={'url': 'YOUR_DASHBOARD_URL'}
)

data = response.json()
print(data)
```

## Step 5: Integrate with Your Flask App

### Option A: Call the API from your app

```python
import requests

# In your Flask route
response = requests.post(
    'http://localhost:5000/scrape',
    json={'url': dashboard_url}
)
data = response.json()
```

### Option B: Use the example integration

```bash
python3 example_integration.py
```

Then call your app's endpoint:
```bash
curl -X POST http://localhost:8000/api/scrape-dashboard \
  -H "Content-Type: application/json" \
  -d '{"dashboard_url": "YOUR_DASHBOARD_URL"}'
```

## Common Issues

### "Connection refused"
- Make sure the scraper is running: `python3 app_v2.py`
- Check the port is 5000

### "Module not found"
- Run setup: `./setup.sh`
- Or install manually: `pip3 install -r requirements.txt`

### "Playwright not found"
- Install browsers: `python3 -m playwright install chromium`

### No data extracted
- Verify the URL is publicly accessible
- Try opening it in your browser first
- Check if it requires login (not supported)

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [example_integration.py](example_integration.py) for integration patterns
- Customize `looker_extractor.py` for your specific dashboard structure

## Production Deployment

For production use:

1. **Disable debug mode** in `app_v2.py`:
   ```python
   app.run(debug=False, host='0.0.0.0', port=5000)
   ```

2. **Use a production WSGI server** (e.g., Gunicorn):
   ```bash
   pip3 install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app_v2:app
   ```

3. **Add rate limiting** to prevent abuse

4. **Set up monitoring** and logging

5. **Use environment variables** for configuration

## Support

- Check the [README.md](README.md) for full documentation
- Run tests: `python3 test_scraper.py`
- Review logs for error messages
