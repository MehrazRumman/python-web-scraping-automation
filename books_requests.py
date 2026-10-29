"""Crawl every book on books.toscrape.com with requests + BeautifulSoup.

Features: session reuse, automatic retries with backoff, a polite delay
between requests, and CSV / JSON export.

    python books_requests.py --out books.csv
    python books_requests.py --out books.json --max-pages 3
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import time
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from parsers import Book, parse_books

START_URL = "https://books.toscrape.com/"
log = logging.getLogger("books")


def make_session() -> requests.Session:
    retry = Retry(total=4, backoff_factor=1.0, status_forcelist=(429, 500, 502, 503, 504))
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers["User-Agent"] = "python-web-scraping-automation/1.0 (+https://github.com/MehrazRumman)"
    return session


def crawl(start_url: str = START_URL, max_pages: int | None = None, delay: float = 0.5) -> list[Book]:
    session = make_session()
    url: str | None = start_url
    books: list[Book] = []
    pages = 0
    while url and (max_pages is None or pages < max_pages):
        resp = session.get(url, timeout=20)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        page_books, url = parse_books(resp.text, resp.url)
        books.extend(page_books)
        pages += 1
        log.info("page %d: %d books (total %d)", pages, len(page_books), len(books))
        if url:
            time.sleep(delay)
    return books


def export(books: list[Book], out: Path) -> None:
    rows = [b.to_row() for b in books]
    if out.suffix == ".json":
        out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        return
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["title"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=Path("books.csv"), help=".csv or .json")
    parser.add_argument("--max-pages", type=int, default=None)
    parser.add_argument("--delay", type=float, default=0.5, help="seconds between requests")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    books = crawl(max_pages=args.max_pages, delay=args.delay)
    export(books, args.out)
    log.info("saved %d books to %s", len(books), args.out)


if __name__ == "__main__":
    main()
