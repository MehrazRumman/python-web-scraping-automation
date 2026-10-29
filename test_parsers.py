"""Offline tests: the HTML below is copied from the live sites, so the
parsers are tested without any network access."""
from decimal import Decimal

from parsers import parse_books, parse_price, parse_quotes

BOOKS_HTML = """
<html><body><ol class="row">
<li><article class="product_pod">
  <p class="star-rating Three"><i class="icon-star"></i></p>
  <h3><a href="catalogue/a-light-in-the-attic_1000/index.html" title="A Light in the Attic">A Light in the ...</a></h3>
  <div class="product_price"><p class="price_color">£51.77</p>
  <p class="instock availability"><i class="icon-ok"></i> In stock </p></div>
</article></li>
<li><article class="product_pod">
  <p class="star-rating One"><i class="icon-star"></i></p>
  <h3><a href="catalogue/tipping-the-velvet_999/index.html" title="Tipping the Velvet">Tipping the Velvet</a></h3>
  <div class="product_price"><p class="price_color">£53.74</p>
  <p class="instock availability"><i class="icon-ok"></i> In stock </p></div>
</article></li>
</ol><ul class="pager"><li class="next"><a href="catalogue/page-2.html">next</a></li></ul></body></html>
"""

QUOTES_HTML = """
<html><body>
<div class="quote"><span class="text">“The world as we have created it is a process of our thinking.”</span>
<span>by <small class="author">Albert Einstein</small></span>
<div class="tags">Tags: <a class="tag">change</a> <a class="tag">thinking</a></div></div>
<nav><ul class="pager"><li class="next"><a href="/js/page/2/">Next</a></li></ul></nav>
</body></html>
"""


def test_parse_price():
    assert parse_price(" £51.77 ") == (Decimal("51.77"), "£")


def test_parse_books():
    books, next_url = parse_books(BOOKS_HTML, "https://books.toscrape.com/")
    assert len(books) == 2
    first = books[0]
    assert first.title == "A Light in the Attic"  # full title from the attribute, not the truncated text
    assert first.price == Decimal("51.77")
    assert first.rating == 3
    assert first.in_stock is True
    assert first.url == "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    assert books[1].rating == 1
    assert next_url == "https://books.toscrape.com/catalogue/page-2.html"


def test_parse_books_last_page():
    html = BOOKS_HTML.replace('<li class="next"><a href="catalogue/page-2.html">next</a></li>', "")
    _, next_url = parse_books(html, "https://books.toscrape.com/catalogue/page-50.html")
    assert next_url is None


def test_parse_quotes():
    quotes, next_url = parse_quotes(QUOTES_HTML, "https://quotes.toscrape.com/js/")
    assert len(quotes) == 1
    assert quotes[0].author == "Albert Einstein"
    assert quotes[0].text.startswith("The world")
    assert quotes[0].tags == ["change", "thinking"]
    assert quotes[0].to_row()["tags"] == "change|thinking"
    assert next_url == "https://quotes.toscrape.com/js/page/2/"
