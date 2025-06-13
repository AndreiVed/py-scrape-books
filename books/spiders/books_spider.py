from typing import Generator

import scrapy
from scrapy.http import Response


class BooksSpiderSpider(scrapy.Spider):
    name = "books_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    raiting_dict = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def parse_detail_book(self, response: Response, **kwargs) -> Generator:
        raiting_str = response.css(
            "p.star-rating::attr(class)"
        ).get().split()[1]
        raiting = self.raiting_dict[raiting_str]

        yield {
            "title": response.css("h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": int(
                response.css(
                    "th:contains('Availability') + td::text"
                ).get().split()[2].strip("(")
            ),
            "rating": raiting,
            "category": response.css(".breadcrumb li a::text").getall()[2],
            "description": response.css(
                "#product_description + p::text").get(),
            "upc": response.css("th:contains('UPC') + td::text").get()
        }

    def parse(self, response: Response, **kwargs) -> Generator:
        book_url_list = response.css(".product_pod a::attr(href)").getall()
        for book_url in book_url_list:
            book_detail_url = response.urljoin(book_url)
            yield scrapy.Request(
                book_detail_url,
                callback=self.parse_detail_book
            )

        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)
