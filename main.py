import argparse
import csv
import datetime
import json
import sys
from pathlib import Path

import feedparser
import requests
import yfinance as yf

BASE_DIR = Path(__file__).parent
WATCHLIST_FILE = BASE_DIR / "watchlist.json"
OUTPUT_STOCKS = BASE_DIR / "output" / "stocks"
OUTPUT_NEWS = BASE_DIR / "output" / "news"

NEWS_FEEDS = {
    "Business & Finance": "https://news.google.com/rss/search?q=business+finance&hl=en-US&gl=US&ceid=US:en",
    "Stock Market": "https://news.google.com/rss/search?q=stock+market&hl=en-US&gl=US&ceid=US:en",
    "Politics & Economy": "https://news.google.com/rss/search?q=politics+economy+policy&hl=en-US&gl=US&ceid=US:en",
    "Trade & Tariffs": "https://news.google.com/rss/search?q=trade+tariffs+sanctions&hl=en-US&gl=US&ceid=US:en",
    "Economic Forecast": "https://news.google.com/rss/search?q=economic+forecast+GDP+inflation+Fed&hl=en-US&gl=US&ceid=US:en",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}


def load_watchlist() -> list[str]:
    if WATCHLIST_FILE.exists():
        with open(WATCHLIST_FILE) as f:
            return json.load(f).get("tickers", [])
    return ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]


def fetch_stocks(tickers: list[str]) -> list[dict]:
    results = []
    for symbol in tickers:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            results.append({
                "symbol": symbol.upper(),
                "price": round(info.last_price, 2),
                "change": round(info.last_price - info.previous_close, 2),
                "change_pct": round((info.last_price - info.previous_close) / info.previous_close * 100, 2),
                "volume": info.last_volume,
            })
        except Exception as e:
            print(f"  [!] Could not fetch {symbol}: {e}", file=sys.stderr)
    return results


def fetch_news(limit: int = 10) -> list[dict]:
    headlines = []
    seen = set()
    for source, url in NEWS_FEEDS.items():
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            feed = feedparser.parse(response.content)
            for entry in feed.entries:
                title = entry.get("title", "")
                if title in seen:
                    continue
                seen.add(title)
                headlines.append({
                    "source": source,
                    "title": title,
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                })
        except Exception as e:
            print(f"  [!] Could not fetch {source}: {e}", file=sys.stderr)
        if len(headlines) >= limit:
            break
    return headlines[:limit]


def print_stocks(stocks: list[dict]):
    print("\n" + "=" * 55)
    print(f"  {'STOCK PRICES':^51}")
    print("=" * 55)
    print(f"  {'Symbol':<10} {'Price':>10} {'Change':>10} {'%':>8}  {'Volume':>12}")
    print("-" * 55)
    for s in stocks:
        print(f"  {s['symbol']:<10} ${s['price']:>9.2f} {s['change']:>+10.2f} {s['change_pct']:>+8.2f}%  {s['volume']:>12,}")
    print("=" * 55)


def print_news(headlines: list[dict]):
    print("\n" + "=" * 55)
    print(f"  {'TOP HEADLINES':^51}")
    print("=" * 55)
    if not headlines:
        print("\n  No headlines available.\n")
    for i, h in enumerate(headlines, 1):
        print(f"\n  [{i}] {h['title']}")
        print(f"      {h['source']}  |  {h['published'][:22] if h['published'] else 'N/A'}")
        print(f"      {h['link']}")
    print("\n" + "=" * 55)


def save_outputs(stocks: list[dict], headlines: list[dict]):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    OUTPUT_STOCKS.mkdir(parents=True, exist_ok=True)
    OUTPUT_NEWS.mkdir(parents=True, exist_ok=True)

    if stocks:
        stocks_file = OUTPUT_STOCKS / f"stocks_{timestamp}.csv"
        with open(stocks_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["symbol", "price", "change", "change_pct", "volume"])
            writer.writeheader()
            writer.writerows(stocks)
        print(f"\n  Saved: {stocks_file}")

    if headlines:
        news_file = OUTPUT_NEWS / f"news_{timestamp}.csv"
        with open(news_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["source", "title", "link", "published"])
            writer.writeheader()
            writer.writerows(headlines)
        print(f"  Saved: {news_file}")


def main():
    parser = argparse.ArgumentParser(description="Stock prices & news headlines fetcher")
    parser.add_argument("tickers", nargs="*", help="Stock tickers (overrides watchlist.json)")
    parser.add_argument("--news", type=int, default=20, metavar="N", help="Number of headlines (default: 20)")
    parser.add_argument("--save", action="store_true", help="Save output to output/stocks/ and output/news/")
    parser.add_argument("--stocks-only", action="store_true", help="Show stocks only")
    parser.add_argument("--news-only", action="store_true", help="Show news only")
    args = parser.parse_args()

    tickers = args.tickers if args.tickers else load_watchlist()
    stocks, headlines = [], []

    if not args.news_only:
        print(f"\n  Fetching prices for: {', '.join(tickers)} ...")
        stocks = fetch_stocks(tickers)
        print_stocks(stocks)

    if not args.stocks_only:
        print(f"\n  Fetching top {args.news} headlines ...")
        headlines = fetch_news(args.news)
        print_news(headlines)

    if args.save:
        save_outputs(stocks, headlines)


if __name__ == "__main__":
    main()
