from src.scraping.providers.provider import Provider
from src.book import Book


class AnnasArchive(Provider):

    def get_search_pages_url(self, query=None, ext=None, lang=None, content=None):
        base_url = "https://annas-archive.org/search"
        url = f"{base_url}?q={query or ''}"
        return [url]

    def find_books_elements(self, soup):
        return soup.find_all("div", class_="h-[125]")

    def parse_book(self, book_el):
        link = self.parse_link(book_el)
        title = self.parse_title(book_el)
        authors = self.parse_authors(book_el)
        release_year = self.parse_release_year(book_el)
        language = self.parse_language(book_el)

        return Book(
            title=title,
            authors=authors,
            release_year=release_year,
            language=language,
            link=link,
        )

    def parse_link(self, book_el):
        link_el = book_el.find("a")
        return "https://annas-archive.org" + link_el["href"]

    def parse_title(self, book_el):
        title_el = book_el.find("h3", class_="truncate text-xl font-bold")
        return title_el.text

    def parse_authors(self, book_el):
        authors_el = book_el.find("div", class_="truncate italic")
        return [authors_el.text]

    def parse_release_year(self, book_el):
        publish_info_el = book_el.find("div", class_="truncate text-sm")
        parts = publish_info_el.text.split(", ")

        year = None
        for part in parts:
            try:
                year = int(part)
            except ValueError:
                pass

        return year

    def parse_language(self, book_el):
        book_meta_el = book_el.find("div", class_="relative top-[-1] pl-4 grow overflow-hidden")
        parts = book_meta_el.text.split(", ")

        language = None
        for part in parts:
            if "[" in part:
                language = part.split("[")[1].strip("]")

        return language
