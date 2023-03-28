import requests
from requests_toolbelt import MultipartEncoder
import time
import json
import datetime as dt

import src.book as book


def get_requests(start_idx=0, end_idx=100, cookie=None, user_agent=None):
    if not cookie or not user_agent:
        raise ValueError("cookie and user_agent must be provided")

    keepGoing = True
    req_books = []

    sess = requests.Session()

    while keepGoing:
        time.sleep(1)
        headers = {
            'cookie': cookie,
            'user-agent': user_agent
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

    return req_books


def filter_requests(req_books, cat_name='Ebooks', filled=0, torsatch=0, lang_codes=['ENG']):
    req_books_reduced = []
    if cat_name:
        req_books_reduced = [x for x in req_books if x['cat_name'].startswith(cat_name)]
    if filled:
        req_books_reduced = [x for x in req_books if x['filled'] == filled]
    if torsatch:
        req_books_reduced = [x for x in req_books if x['torsatch'] == torsatch]
    if lang_codes:
        req_books_reduced = [x for x in req_books if x['lang_code'] in lang_codes]

    return req_books_reduced


def save_requests(req_books, filepath='requests.json'):
    with open(filepath, 'w') as f:
        json.dump(req_books, f, indent=2)

def load_requests(filepath='requests.json'):
    with open(filepath, 'r') as f:
        return json.load(f)


def convert_requests_to_book(req_books):
    books = []
    for req_book in req_books:
        book = get_book_from_request(req_book)
        books.append(book)
    return books


def get_book_from_request(req_book):
    title = req_book['title']
    authors = get_authors_from_request(req_book)
    language = req_book['lang_code']
    release_year = get_release_year_from_request(req_book)
    link = None
    return book.Book(title, authors, language, release_year, link)


def get_authors_from_request(req_book):
    authors = []
    try:
        authors_json = json.loads(req_book['authors'])
        authors = [v for k, v in authors_json.items()]
    except:
        pass
    return authors


def get_release_year_from_request(req_book):
    release_year = None
    try:
        release_date = dt.datetime.strptime(req_book['releasedate'], '%Y-%m-%d')
        release_year = release_date.year
    except:
        pass
    return release_year