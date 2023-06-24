import requests
from requests_toolbelt import MultipartEncoder
import time
import json
import datetime as dt
import yaml

import src.book as book


class MyAnonamouse:

    def __init__(self):
        self._config = self._load_config()
        self._cookie = self._config['mam']['cookie']
        self._user_agent = self._config['mam']['user_agent']

        self._req_books = []
        self.books = []

    def _load_config(self, filepath='config.yaml'):
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)

    def get_requested_books(self, start_idx=0, end_idx=None, cat_name='Ebooks', filled=0, torsatch=0, lang_codes=['ENG']):
        self._load_requests(start_idx, end_idx)
        self._filter_requests(cat_name, filled, torsatch, lang_codes)
        self._convert_requests_to_books()
        return self.books

    def _load_requests(self, start_idx=0, end_idx=100):
        if not self._cookie or not self._user_agent:
            raise ValueError("cookie and user_agent must be provided")

        keepGoing = True
        req_books = []

        sess = requests.Session()

        while keepGoing:
            time.sleep(self._config['mam']['request_delay'])
            headers = {
                'cookie': self._cookie,
                'user-agent': self._user_agent
            }

            params = {
                'tor[text]': '',
                'tor[srchIn][title]': 'true',
                'tor[viewType]': 'unful',
                'tor[cat][]': 'm14',  # search ebooks category
                'tor[startDate]': '',
                'tor[endDate]': '',
                'tor[startNumber]': f'{start_idx}',
                'tor[sortType]': 'dateD'
            }
            data = MultipartEncoder(fields=params)
            headers['Content-type'] = data.content_type
            api_url = 'https://www.myanonamouse.net/tor/json/loadRequests.php'
            r = sess.post(api_url, headers=headers, data=data)

            req_books += r.json()['data']
            total_items = r.json()['found']

            start_idx += 100
            end_idx = min(end_idx or total_items, total_items)
            keepGoing = start_idx < end_idx and start_idx < total_items
            print(f"{start_idx} of {total_items} items fetched")

        self._req_books = req_books
        return req_books

    def _filter_requests(self, cat_name='Ebooks', filled=0, torsatch=0, lang_codes=['ENG']):
        req_books = self._req_books
        req_books_reduced = []
        if cat_name:
            req_books_reduced = [x for x in req_books if x['cat_name'].startswith(cat_name)]
        if filled:
            req_books_reduced = [x for x in req_books if x['filled'] == filled]
        if torsatch:
            req_books_reduced = [x for x in req_books if x['torsatch'] == torsatch]
        if lang_codes:
            req_books_reduced = [x for x in req_books if x['lang_code'] in lang_codes]

        self.req_books = req_books_reduced
        return req_books_reduced

    def _convert_requests_to_books(self):
        books = []
        for req_book in self._req_books:
            book = self._get_book_from_request(req_book)
            books.append(book)

        self.books = books
        return books

    def _get_book_from_request(self, req_book):
        title = req_book['title']
        authors = self._get_authors_from_request(req_book)
        language = self._get_language_from_request(req_book)
        release_year = self._get_release_year_from_request(req_book)
        link = None
        return book.Book(title, authors, language, release_year, link)

    def _get_authors_from_request(self, req_book):
        authors = []
        try:
            authors_json = json.loads(req_book['authors'])
            authors = [v for k, v in authors_json.items()]
        except:
            pass
        return authors

    def _get_release_year_from_request(self, req_book):
        release_year = None
        try:
            release_date = dt.datetime.strptime(req_book['releasedate'], '%Y-%m-%d')
            release_year = release_date.year
        except:
            pass
        return release_year

    def _get_language_from_request(self, req_book):
        return req_book['lang_code'][:2]
