# USPTO Newsletter Backend

## Setup
1. Create virtual environment: `python -m venv venv`
2. Activate virtual environment: `.env\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy .env.example to .env and fill in required values

## Development
- Run tests: `pytest`
- Generate newsletter: `python -m src.main`
- Run scheduler: `python scripts/run_scheduler.py`

## Features
- Daily article scanning from various sources
- Monthly newsletter compilation
- Multiple output formats (HTML, Markdown, Email)
- Subscriber management
- Automated scheduling

## Directory Structure
- `data/daily_scans/`: Stores daily article scans
- `data/generated/`: Stores generated newsletters
- `newsletters/`: Final newsletter output
- `logs/`: Application logs

## Configuration
The scheduler can be configured through environment variables:
- `SCAN_INTERVAL_HOURS`: Time between scans (default: 24)
- `SMTP_SERVER`: Email server for sending newsletters
- `SMTP_PORT`: Email server port
- `SMTP_USERNAME`: Email server username
- `SMTP_PASSWORD`: Email server password
