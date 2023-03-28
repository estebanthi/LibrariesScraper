import time
import json

from src.scraping.providers.annasarchive import AnnasArchive
from src.scraping.providers.pdfdrive import PdfDrive
import src.scraping.scraper as scraper
import src.matcher as matcher
import src.mam as mam
import src.json_encoder as json_encoder

if __name__ == "__main__":
    providers = [PdfDrive()]
    threshold = 0.8
    match_filepath = "out/matches.json"

    requests = mam.load_requests("out/requests.json")
    requests = mam.filter_requests(requests, cat_name='Ebooks', filled=0, torsatch=0, lang_codes=None)
    mam_books = mam.convert_requests_to_book(requests)[0:100]

    matcher = matcher.Matcher()
    matched_books = []
    for book in mam_books:
        search_query = book.title
        search_results = scraper.search(providers, query=search_query)
        if search_results:
            match_result = matcher.match(book, search_results, threshold)
            if match_result:
                matched_books.append([book, match_result])
                print(f"Found a match for {book.title} by {book.authors} ({book.language})")

        time.sleep(1)

    with open(match_filepath, 'w') as f:
        json.dump(matched_books, f, indent=2, cls=json_encoder.DataclassJSONEncoder)
