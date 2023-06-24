# BooksScraper

BooksScraper is a Python project to scrape books from various sources. For now, it can scrape books from:
- [Anna's Archive](https://annas-archive.org)
- [PDF Drive](https://www.pdfdrive.com)

## Scraping Books

```python
from src.scraping import Scraper
from src.scraping.providers import AnnasArchive, PdfDrive

providers = [AnnasArchive(), PdfDrive()]
scraper = Scraper(providers)

books = scraper.search(query='python', ext='epub', lang='en', content='book_any', pubyear='2015')
```

You can then save the result:
```python
from src.books import BooksFS

books_fs = BooksFS()

filepath = 'books.pkl'
books_fs.save(books, filepath)
books = books_fs.load(filepath)
```

A default filepath is provided in a `config.yaml` file:
```yaml
books_fs:
  filepath: ./data/books.pkl
```

## Books Matching

When scraping books, you will probably get too much results you don't want if your query isn't specific enough. The `BooksMatcher` class helps to filter the results by matching a given book with a list of books according to some criteria.

```python
from src.books import BooksMatcher

books_matcher = BooksMatcher()
matches = books_matcher.find_matches(reference_book, scraped_books, threshold=0.8)  # find books with a similarity score > 80%
```

You can disable some criteria at the initialization of the class:
```python
from src.books import BooksMatcher

books_matcher = BooksMatcher(language_enabled=False)  # disable language criterion
```


## MyAnonamouse

LibrariesScraper provides an interface with MAM to fetch requested books.

```python
from src.interfaces import MyAnonamouse

mam = MyAnonamouse()
books = mam.get_requested_books()
```

To use the interface, you need to provide your cookie and user agent in the `config.yaml` file (you get them from Developer Tools in your browser).

```yaml
mam:
  cookie: <cookie>
  user_agent: <user_agent>
  request_delay: 0.2  # time between each request to MAM
```