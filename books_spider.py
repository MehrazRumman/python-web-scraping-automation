"""Scrapy spider for books.toscrape.com: listing pages plus every detail page.

Run it without creating a Scrapy project:

    scrapy runspider books_spider.py -O books.jsonl

Scrapy handles concurrency, retries, throttling and export for you. This
spider also follows each book to its detail page to collect the UPC,
category, stock count and description.
"""
from __future__ import annotations

import re

import scrapy

RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    custom_settings = {
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 4,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 8,
        "RETRY_TIMES": 3,
        "ROBOTSTXT_OBEY": True,
        "FEED_EXPORT_ENCODING": "utf-8",
        "USER_AGENT": "python-web-scraping-automation/1.0 (+https://github.com/MehrazRumman)",
    }

    def parse(self, response):
        for href in response.css("article.product_pod h3 a::attr(href)").getall():
            yield response.follow(href, callback=self.parse_book)
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        table = {
            row.css("th::text").get(): row.css("td::text").get()
            for row in response.css("table.table-striped tr")
        }
        stock_text = table.get("Availability", "")
        stock = re.search(r"(\d+)", stock_text)
        rating_class = response.css("p.star-rating::attr(class)").get(default="")
        yield {
            "title": response.css("div.product_main h1::text").get(),
            "price": response.css("div.product_main p.price_color::text").get(),
            "rating": next((RATINGS[c] for c in rating_class.split() if c in RATINGS), 0),
            "upc": table.get("UPC"),
            "category": response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
            "stock": int(stock.group(1)) if stock else 0,
            "description": response.css("#product_description + p::text").get(),
            "url": response.url,
        }
