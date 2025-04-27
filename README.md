# OSINT Microagent

A Python-based OSINT (Open Source Intelligence) microagent that performs comprehensive public information searches across multiple sources with results categorization and webhook integration.

## Features

- **Multiple Query Types**: Process various input types (names, emails, phone numbers, usernames, domains, IPs)
- **Search Engine Scraping**: Extract data from DuckDuckGo and other search engines
- **API Integration**: Connect with free-tier APIs like IPinfo.io, Hunter.io, and HaveIBeenPwned
- **WHOIS Lookups**: Perform domain and IP WHOIS lookups
- **Intelligent Filtering**: Filter out ads, duplicates, and irrelevant content
- **Result Categorization**: Organize findings into emails, phone numbers, social links, etc.
- **Webhook Export**: Send results to configurable webhook endpoints (for n8n integration)
- **Database Logging**: Store queries and results in a SQL database

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure API keys in `.env` file
4. Run the application: `python -m main`

## Environment Variables

Add the following to your `.env` file:

```
# API Keys for external services
IPINFO_API_KEY=your_ipinfo_api_key
HUNTER_API_KEY=your_hunter_api_key
HIBP_API_KEY=your_haveibeenpwned_api_key

# Default webhook URL (for n8n integration)
DEFAULT_WEBHOOK_URL=your_default_webhook_url

# Database URL
DATABASE_URL=your_database_url
```

## API Usage

### Web Interface

Visit `http://localhost:8000` in your browser.

### API Endpoint

Make a GET request to:

```
http://localhost:8000/api/search?query=your_query&webhook_url=optional_webhook_url
```

## Response Format

```json
{
  "query": "example.com",
  "query_type": "domain",
  "results": {
    "emails": [],
    "phone_numbers": [],
    "social_links": [],
    "addresses": [],
    "business_info": [],
    "leaks": [],
    "raw_results": [],
    "domains": [],
    "ips": [],
    "summary": "Executive Summary"
  }
}
```

## Project Structure

- `app/`: Main application package
  - `handlers/`: Input processing and validation
  - `scrapers/`: Data collection modules
  - `parsers/`: Result processing and categorization
  - `exporters/`: Output formatting and delivery
- `templates/`: HTML templates for web interface
- `static/`: CSS, JavaScript, and other static assets
- `main.py`: Application entry point

## License

MIT