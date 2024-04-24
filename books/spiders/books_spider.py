import scrapy
from scrapy.http import Response

from books.spiders.utils import BookScraper


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.base_url = "https://books.toscrape.com/catalogue/"

    def parse(self, response: Response, **kwargs) -> scrapy.Request:
        next_page = response.css("li.next > a::attr(href)").get()
        urls = self._get_page_urls(response)

        for book_url in urls:
            yield scrapy.Request(book_url, callback=self._scrape_single_book)

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _get_page_urls(self, response: Response) -> list[str]:
        return [
            self.base_url + url
            for url in response.css("article > h3 > a::attr(href)").getall()
        ]

    @staticmethod
    def _scrape_single_book(response: Response) -> dict:
        book_scraper = BookScraper(response)

        yield dict(
            title=book_scraper.get_title(),
            price=book_scraper.get_price(),
            amount_in_stock=book_scraper.get_amount_in_stock(),
            rating=book_scraper.get_rating(),
            category=book_scraper.get_category(),
            description=book_scraper.get_description(),
            upc=book_scraper.get_upc()
        )
