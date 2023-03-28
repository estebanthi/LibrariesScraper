from abc import ABC, abstractmethod
import urllib.parse
import requests
from bs4 import BeautifulSoup

from src.book import Book


class Provider(ABC):

    def search(self, query=None, ext=None, lang=None, content=None):
        pages_url = self.get_search_pages_url(query, ext, lang, content)
        pages_url = [self.format_url(url) for url in pages_url]

        books = []
        for page_url in pages_url:
            books.extend(self.search_page(page_url))

        return books

    def search_page(self, url):
        r = requests.get(url)
        html = self.remove_comments_from_html(r.text)
        soup = BeautifulSoup(html, "html.parser")

        books_el = self.find_books_elements(soup)
        books = [self.parse_book(book_el) for book_el in books_el]
        return books

    @abstractmethod
    def get_search_pages_url(self, query=None, ext=None, lang=None, content=None):
        pass

    @abstractmethod
    def find_books_elements(self, soup):
        pass

    @abstractmethod
    def parse_book(self, book_el) -> Book:
        pass

    def format_url(self, url):
        return urllib.parse.quote(url, safe=":/?=").replace("%26", "&")

    @staticmethod
    def remove_comments_from_html(html):
        return html.replace("<!--", "").replace("-->", "")
