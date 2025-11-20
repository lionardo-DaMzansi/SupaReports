# Azi — SupaChat Data Analyst Agent (Local)

A local Flask-based implementation of the Azi data analyst agent using OpenAI's Assistants API.

## Features

- ✅ **Enhanced UI** with progress indicators and structured result rendering
- ✅ **Robust error handling** with detailed validation
- ✅ **File upload support** for CSV, XLSX, PDF, and more
- ✅ **OpenAI Assistants API** with web_search, file_search, and code_interpreter tools
- ✅ **Structured JSON output** following the defined schema
- ✅ **Assistant reuse** to save on API costs
- ✅ **Production-ready server** using Waitress

## Quick Start

### 1. Set Up Python Environment

```bash
cd supachat-azi-local
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Edit the `.env` file and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
MODEL_ID=gpt-4o
ASSISTANT_ID=
PORT=5173
DEBUG=False
```

**Important:** Replace `sk-your-actual-api-key-here` with your actual OpenAI API key.

### 4. Add Your System Prompt and Schema

Open `app.py` and replace the placeholder content in these two sections:

1. **SYSTEM_PROMPT** (around line 37):
   - Replace the placeholder with your complete Azi system prompt
   - This defines the agent's behavior and instructions

2. **OUTPUT_SCHEMA** (around line 48):
   - Replace with your complete output schema definition
   - This ensures structured JSON responses

### 5. Run the Server

```bash
python app.py
```

The server will start at **http://localhost:5173**

On first run, a new Assistant will be created and its ID will be printed. Add this ID to your `.env` file as `ASSISTANT_ID` to reuse the same assistant on subsequent runs.

## Usage

1. Open http://localhost:5173 in your browser
2. Fill out the briefing form:
   - **Core Briefing**: Brand, Market, Reporting Period, Objective (all required)
   - **Competitors**: JSON array with competitor names and optional social handles
   - **Additional Context**: Dashboard links, research URLs, hypotheses (optional)
   - **Data Upload**: Upload CSV, XLSX, or PDF files (optional)
3. Click **Run Analysis**
4. Wait for the analysis to complete (progress indicator will show)
5. View structured results or download as JSON

## Project Structure

```
supachat-azi-local/
├── app.py                  # Main Flask application with enhanced error handling
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration (DO NOT COMMIT)
├── .env.template          # Template for environment variables
├── README.md              # This file
└── static/
    └── index.html         # Enhanced UI with progress indicators
```

## API Endpoints

### `GET /`
Serves the main HTML interface

### `GET /api/health`
Health check endpoint
- Returns server status, model info, and configuration

### `POST /api/analyze`
Main analysis endpoint
- **Content-Type**: `multipart/form-data`
- **Form Fields**:
  - `brand` (required): Brand name
  - `market` (required): Target market
  - `reporting_period` (required): Date range
  - `objective` (required): Campaign objective
  - `competitors` (optional): JSON array of competitors
  - `dashboard_links` (optional): Comma-separated URLs
  - `research_urls` (optional): Comma-separated URLs
  - `hypotheses` (optional): Comma-separated hypotheses
  - `data_file` (optional): File upload
- **Response**: Structured JSON with analysis results

## Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | - | Yes |
| `MODEL_ID` | OpenAI model to use | `gpt-4o` | No |
| `ASSISTANT_ID` | Existing assistant ID to reuse | (empty) | No |
| `PORT` | Server port | `5173` | No |
| `DEBUG` | Enable debug mode | `False` | No |

### File Upload Limits

- **Max file size**: 50MB
- **Allowed extensions**: `.csv`, `.xlsx`, `.xls`, `.pdf`, `.txt`, `.json`

## Error Handling

The application includes comprehensive error handling:

- ✅ Form validation with detailed error messages
- ✅ File type and size validation
- ✅ OpenAI API error handling
- ✅ Timeout handling (5 minutes default)
- ✅ JSON parsing error recovery
- ✅ Graceful degradation with raw response fallback

## Troubleshooting

### "Please set OPENAI_API_KEY in your .env file"
- Edit `.env` and add your OpenAI API key
- Make sure there are no quotes around the key

### "File too large" error
- The default limit is 50MB
- Modify `MAX_FILE_SIZE` in `app.py` if needed

### Analysis times out
- Increase the timeout in `poll_run_status()` (default: 300 seconds)
- Consider using a more powerful model

### "Response was not valid JSON"
- Check your OUTPUT_SCHEMA definition
- Review the system prompt to ensure it emphasizes JSON output
- Check the raw response in the error message for debugging

### Assistant creation fails
- Verify your OpenAI API key has access to Assistants API
- Check that the model supports the tools you're using
- Ensure your schema is valid JSON Schema format

## Development

### Enable Debug Mode

Set `DEBUG=True` in `.env` to get detailed error traces in the console.

### Testing Locally

```bash
# Health check
curl http://localhost:5173/api/health

# Test analysis (with minimal data)
curl -X POST http://localhost:5173/api/analyze \
  -F "brand=TestBrand" \
  -F "market=US" \
  -F "reporting_period=2025-01-01 to 2025-01-31" \
  -F "objective=Awareness"
```

## Security Notes

⚠️ **Important**: This is a local development setup. Before deploying to production:

1. Add authentication/authorization
2. Implement rate limiting
3. Add HTTPS support
4. Validate and sanitize all inputs
5. Set up proper CORS policies
6. Use environment-specific configurations
7. Never commit `.env` files to version control

## Author

**Lindile Ndube**
Owner & Developer

## License

Proprietary - SupaChat

## Support

For issues or questions, contact your development team.
