# Python Web Scraping & Automation Examples

![tests](https://github.com/MehrazRumman/python-web-scraping-automation/actions/workflows/tests.yml/badge.svg)

Three ways to scrape websites with Python, side by side: **requests + BeautifulSoup**, **Playwright** for JavaScript-rendered pages, and a **Scrapy** spider for full crawls. They run against [books.toscrape.com](https://books.toscrape.com) and [quotes.toscrape.com](https://quotes.toscrape.com), which are sandbox sites built for scraping practice.

Written by [Mehraz Hossain Rumman](https://mehrazrumman.github.io/), a Python software engineer and web scraping / automation developer (Scrapy contributor).

## Which tool when?

| Script | Tool | Use it when |
|---|---|---|
| `books_requests.py` | requests + BeautifulSoup | The HTML already has the data. Fast, light, simple. |
| `quotes_playwright.py` | Playwright (headless Chromium) | The page builds content with JavaScript, needs clicks, logins or scrolling. |
| `books_spider.py` | Scrapy | Thousands of pages: built-in concurrency, retries, throttling, robots.txt and export. |

All three share `parsers.py`, so the parsing logic is written once and unit tested offline.

## Quick start

```bash
pip install -r requirements.txt
playwright install chromium

# 1. requests + BeautifulSoup: every book on the site to CSV (or .json)
python books_requests.py --out books.csv

# 2. Playwright: JavaScript-rendered quotes
python quotes_playwright.py --out quotes.csv --max-pages 3

# 3. Scrapy: listing + detail pages (UPC, category, stock, description)
scrapy runspider books_spider.py -O books.jsonl

# tests (no network needed)
pytest -q
```

## What the code shows

- Pagination by following the "next" link until the last page
- Retries with exponential backoff on 429 / 5xx (`urllib3.Retry`)
- A polite delay and an honest User-Agent; the Scrapy spider obeys `robots.txt` and uses AutoThrottle
- Blocking images and fonts in Playwright to load pages faster
- Clean typed output (`dataclass`, `Decimal` prices, ratings as numbers) exported to CSV / JSON
- Parsers kept separate from fetching, tested with saved HTML in CI

## Scraping responsibly

Check a site's terms and `robots.txt`, keep request rates low, don't collect personal data, and use an official API when one exists.

## Need a scraper or automation?

I build custom Python scrapers, data pipelines and workflow automation (Scrapy, Playwright, Celery, Django, FastAPI). I also tutor Python.

- Portfolio: https://mehrazrumman.github.io/
- LinkedIn: https://www.linkedin.com/in/mehraz-rumman/
- Email: mehrazrumman@gmail.com

## License

MIT
