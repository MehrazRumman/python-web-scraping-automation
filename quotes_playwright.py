"""Scrape a JavaScript-rendered site with Playwright (headless Chromium).

quotes.toscrape.com/js/ builds its HTML in the browser, so plain
requests sees no quotes. Playwright runs the page, waits for the content,
then hands the rendered HTML to the same BeautifulSoup parser.

    pip install -r requirements.txt && playwright install chromium
    python quotes_playwright.py --out quotes.csv
"""
from __future__ import annotations

import argparse
import csv
import logging
from pathlib import Path

from playwright.sync_api import sync_playwright

from parsers import Quote, parse_quotes

START_URL = "https://quotes.toscrape.com/js/"
log = logging.getLogger("quotes")


def crawl(start_url: str = START_URL, max_pages: int | None = None) -> list[Quote]:
    quotes: list[Quote] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Skip images and fonts: faster, and lighter on the target site.
        page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2}", lambda route: route.abort())
        url: str | None = start_url
        pages = 0
        while url and (max_pages is None or pages < max_pages):
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_selector("div.quote", timeout=15_000)
            page_quotes, url = parse_quotes(page.content(), page.url)
            quotes.extend(page_quotes)
            pages += 1
            log.info("page %d: %d quotes (total %d)", pages, len(page_quotes), len(quotes))
        browser.close()
    return quotes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=Path("quotes.csv"))
    parser.add_argument("--max-pages", type=int, default=None)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    quotes = crawl(max_pages=args.max_pages)
    with args.out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["text", "author", "tags"])
        writer.writeheader()
        writer.writerows(q.to_row() for q in quotes)
    log.info("saved %d quotes to %s", len(quotes), args.out)


if __name__ == "__main__":
    main()
