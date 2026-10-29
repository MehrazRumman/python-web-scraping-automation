"""HTML parsers shared by every scraper in this repo.

Keeping parsing separate from fetching makes the logic easy to unit test
with saved HTML, and lets the same code run behind requests, Playwright
or Scrapy.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from decimal import Decimal
from urllib.parse import urljoin

from bs4 import BeautifulSoup

RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


@dataclass
class Book:
    title: str
    price: Decimal
    currency: str
    rating: int
    in_stock: bool
    url: str

    def to_row(self) -> dict:
        row = asdict(self)
        row["price"] = str(self.price)
        return row


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str] = field(default_factory=list)

    def to_row(self) -> dict:
        return {"text": self.text, "author": self.author, "tags": "|".join(self.tags)}


def parse_price(raw: str) -> tuple[Decimal, str]:
    """'£51.77' -> (Decimal('51.77'), '£')"""
    raw = raw.strip()
    digits = "".join(ch for ch in raw if ch.isdigit() or ch == ".")
    currency = "".join(ch for ch in raw if not (ch.isdigit() or ch == ".")).strip()
    return Decimal(digits), currency


def parse_books(html: str, page_url: str) -> tuple[list[Book], str | None]:
    """Parse a books.toscrape.com listing page.

    Returns the books on the page and the absolute URL of the next page
    (or None on the last page).
    """
    soup = BeautifulSoup(html, "lxml")
    books: list[Book] = []
    for card in soup.select("article.product_pod"):
        link = card.select_one("h3 a")
        price, currency = parse_price(card.select_one("p.price_color").get_text())
        rating_classes = card.select_one("p.star-rating")["class"]
        rating = next((RATINGS[c] for c in rating_classes if c in RATINGS), 0)
        stock = card.select_one("p.availability")
        books.append(
            Book(
                title=link.get("title") or link.get_text(strip=True),
                price=price,
                currency=currency,
                rating=rating,
                in_stock=bool(stock and "in stock" in stock.get_text().lower()),
                url=urljoin(page_url, link["href"]),
            )
        )
    next_link = soup.select_one("li.next a")
    next_url = urljoin(page_url, next_link["href"]) if next_link else None
    return books, next_url


def parse_quotes(html: str, page_url: str) -> tuple[list[Quote], str | None]:
    """Parse a quotes.toscrape.com page (after JavaScript has rendered it)."""
    soup = BeautifulSoup(html, "lxml")
    quotes = [
        Quote(
            text=q.select_one("span.text").get_text(strip=True).strip("“”"),
            author=q.select_one("small.author").get_text(strip=True),
            tags=[t.get_text(strip=True) for t in q.select("a.tag")],
        )
        for q in soup.select("div.quote")
    ]
    next_link = soup.select_one("li.next a")
    next_url = urljoin(page_url, next_link["href"]) if next_link else None
    return quotes, next_url
