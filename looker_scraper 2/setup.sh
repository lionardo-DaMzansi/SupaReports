#!/bin/bash

echo "Setting up Looker Studio Scraper..."

# Install Python dependencies
echo "Installing Python packages..."
pip3 install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
python3 -m playwright install chromium

echo ""
echo "Setup complete!"
echo ""
echo "To start the server, run:"
echo "  python3 app.py"
echo ""
echo "The API will be available at http://localhost:5000"
