from abc import ABC, abstractmethod
import urllib.parse
import requests
from bs4 import BeautifulSoup

from src.books.book import Book


class Provider(ABC):

    def search(self, query=None, ext=None, lang=None, content=None, pubyear=None):
        pages_url = self._get_search_pages_url(query, ext, lang, content, pubyear)
        pages_url = [self._format_url(url) for url in pages_url]

        books = []
        for page_url in pages_url:
            books.extend(self._search_page(page_url))

        return books

    def _search_page(self, url):
        r = requests.get(url)
        html = self._remove_comments_from_html(r.text)
        soup = BeautifulSoup(html, "html.parser")

        books_el = self._find_books_elements(soup)
        books = [self._parse_book(book_el) for book_el in books_el]
        return books

    @abstractmethod
    def _get_search_pages_url(self, query=None, ext=None, lang=None, content=None):
        pass

    @abstractmethod
    def _find_books_elements(self, soup):
        pass

    @abstractmethod
    def _parse_book(self, book_el) -> Book:
        pass

    def _format_url(self, url):
        return urllib.parse.quote(url, safe=":/?=").replace("%26", "&")

    def _remove_comments_from_html(self, html):
        return html.replace("<!--", "").replace("-->", "")
