# stock-news-fetcher

A CLI tool that fetches live stock prices and market-relevant news headlines from the terminal.

## Features

- Live stock prices with price change and volume via `yfinance`
- News headlines across 5 categories: Business & Finance, Stock Market, Politics & Economy, Trade & Tariffs, and Economic Forecast
- Watchlist managed via `watchlist.json` — no code changes needed to add tickers
- Optional CSV export to `output/stocks/` and `output/news/`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# Fetch stocks + news (uses watchlist.json)
python main.py

# Save output to CSV
python main.py --save

# Stocks only
python main.py --stocks-only

# News only
python main.py --news-only

# Override watchlist with specific tickers
python main.py NVDA META NFLX

# Control number of headlines
python main.py --news 30
```

## Watchlist

Edit `watchlist.json` to manage your default tickers:

```json
{
  "tickers": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
}
```

## Output

CSV files are saved with timestamps and ignored by git:

```
output/
├── stocks/stocks_YYYYMMDD_HHMMSS.csv
└── news/news_YYYYMMDD_HHMMSS.csv
```
