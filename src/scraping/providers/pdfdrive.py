import requests
from bs4 import BeautifulSoup

from src.scraping.providers.provider import Provider
from src.book import Book


class PdfDrive(Provider):
    """ Slow provider as for each book it needs to make a request to get the details. """

    def __init__(self, exact_match=True, max_pages=2):
        super().__init__()
        self.exact_match = exact_match
        self.max_pages = max_pages

    def _get_search_pages_url(self, query=None, ext=None, lang=None, content=None, pubyear=None):
        base_url = "https://www.pdfdrive.com/search?q="
        url = f"{base_url}{query or ''}&em={1 if self.exact_match else 0}&searchin={lang or ''}&pubyear={pubyear or ''}"
        nb_pages = min(self._get_nb_pages(url), self.max_pages)
        return [f"{url}&page={page}" for page in range(1, nb_pages + 1)]

    def _get_nb_pages(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        pagination_el = soup.find("div", class_="Zebra_Pagination")

        if not pagination_el:
            return 1

        last_page_el = pagination_el.find_all("a")[-1]
        if last_page_el.text == "Next":
            return int(pagination_el.find_all("a")[-2].text)
        return int(last_page_el.text)

    def _find_books_elements(self, soup):
        files_new_el = soup.find("div", class_="files-new")
        if files_new_el:
            return files_new_el.find_all("li")
        return []

    def _parse_book(self, book_el):
        book_link = book_el.find("a")
        book_url = "https://www.pdfdrive.com" + book_link["href"]
        response = requests.get(book_url)
        book_el = BeautifulSoup(response.text, "html.parser").find("div", class_="ebook-main")

        link = book_url
        title = self._parse_title(book_el)
        authors = self._parse_authors(book_el)
        release_year = self._parse_release_year(book_el)
        language = self._parse_language(book_el)

        return Book(
            title=title,
            authors=authors,
            release_year=release_year,
            language=language,
            link=link,
        )

    def _parse_title(self, book_el):
        title_el = book_el.find("h1", class_="ebook-title")
        if title_el.text.startswith('"') and title_el.text.endswith('"'):
            return title_el.text[1:-1]
        return title_el.text

    def _parse_authors(self, book_el):
        authors_el = book_el.find("span", itemprop="creator")
        return [authors_el.text] if authors_el else []

    def _parse_release_year(self, book_el):
        publish_info_el = book_el.find("div", class_="ebook-file-info")
        parts = publish_info_el.find_all("span", class_="info-green")

        year = None
        for part in parts:
            try:
                year = int(part.text)
            except Exception:
                pass

        return year

    def _parse_language(self, book_el):
        publish_info_el = book_el.find("div", class_="ebook-file-info")
        parts = publish_info_el.find_all("span", class_="info-green")

        return parts[-1].text[:2]
