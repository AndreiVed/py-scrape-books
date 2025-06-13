from typing import Generator, re

import scrapy
from scrapy.http import Response

from books.items import BooksItem


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
        title = response.css("h1::text").get()
        price = float(
            response.css(".price_color::text").get().replace("£", "")
        )
        # amount_in_stock = int(
        #         response.css(
        #             "th:contains('Availability') + td::text"
        #         ).get().split()[2].strip("(")
        #     )
        availability_text = response.css(
            "th:contains('Availability') + td::text"
        ).get()
        amount_in_stock = None
        if availability_text:
            match = re.search(
                r"\((\d+)\s*available\)",
                availability_text,
                re.IGNORECASE
            )
            if match:
                amount_in_stock = int(match.group(1))

        raiting_str = response.css(
            "p.star-rating::attr(class)"
        ).get().split()[1]
        raiting = self.raiting_dict[raiting_str]
        category = response.css(
            ".breadcrumb li:nth-last-child(2) a::text"
        ).get()

        description = response.css(
            "#product_description + p::text"
        ).get()

        upc = response.css("th:contains('UPC') + td::text").get()

        yield BooksItem(
            title=title,
            price=price,
            amount_in_stock=amount_in_stock,
            raiting=raiting,
            category=category,
            description=description,
            upc=upc
        )

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
