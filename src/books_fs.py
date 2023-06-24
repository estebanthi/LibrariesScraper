import yaml
from src.book import Book
import pickle


class BooksFS:

        def __init__(self, filepath=None):
            self.filepath = filepath or self._load_config()['book_saver']['filepath']

        def _load_config(self, filepath='config.yaml'):
            with open(filepath, 'r') as f:
                return yaml.safe_load(f)

        def save_books(self, books):
            with open(self.filepath, 'wb') as f:
                pickle.dump(books, f)

        def load_books(self):
            with open(self.filepath, 'rb') as f:
                return pickle.load(f)
