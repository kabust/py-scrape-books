from pathlib import Path

import requests
import scrapy
from scrapy.http import Response, HtmlResponse


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = "https://books.toscrape.com/catalogue/"

    def parse(self, response: Response, **kwargs):
        next_page = response.css("li.next > a::attr(href)").get()
        urls = self._get_page_urls(response)

        for book_url in urls:
            yield scrapy.Request(book_url, callback=self._scrape_single_book)

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _get_page_urls(self, response: Response) -> [str]:
        return [
            self.base_url + url
            for url in response.css("article > h3 > a::attr(href)").getall()
        ]

    def _scrape_single_book(self, response: Response) -> dict:
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }

        amount_in_stock = response.css("tr:nth-child(6) > td::text").extract_first().split()[2][1:]

        yield dict(
            title=response.css(".product_main > h1::text").get(),
            price=float(response.css(".price_color::text").get()[2:]),
            amount_in_stock=int(amount_in_stock) if amount_in_stock is not None else 0,
            rating=int(rating_map[response.css(".star-rating::attr(class)").get().split()[-1]]),
            category=response.css(".breadcrumb > li:nth-child(3) > a::text").get(),
            description=response.css("#content_inner > article > p::text").get(),
            upc=response.css("tr:nth-child(1) > td::text").extract_first()
        )
