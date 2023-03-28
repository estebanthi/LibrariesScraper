from src.scraping.providers.annasarchive import AnnasArchive
import src.scraping.scraper as scraper
import src.matcher as matcher
import src.mam as mam

if __name__ == "__main__":
    providers = [AnnasArchive()]

    requests = mam.load_requests("out/requests.json")
    requests = mam.filter_requests(requests, cat_name='Ebooks', filled=0, torsatch=0, lang_codes=None)
    print(f"{len(requests)} requests loaded")

    mam_books = mam.convert_requests_to_book(requests)
