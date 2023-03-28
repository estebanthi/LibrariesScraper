import requests
from bs4 import BeautifulSoup
import urllib.parse
import json
import time
import webbrowser

def parse_book(book_el):
    link_el = book_el.find("a")["href"]
    link = parse_link(link_el)

    book_meta_el = book_el.find("div", class_="relative top-[-1] pl-4 grow overflow-hidden")
    language, book_type, size_mb = parse_book_meta(book_meta_el)

    title = book_el.find("h3", class_="truncate text-xl font-bold").text

    publish_info_el = book_el.find("div", class_="truncate text-sm")
    publisher, year = parse_publish_info(publish_info_el)

    author = book_el.find("div", class_="truncate italic").text

    return {
        "title": title,
        "link": link,
        "authors": [author],
        "language": language,
        "book_type": book_type,
        "size_mb": size_mb,
        "publisher": publisher,
        "year": year,
    }

def parse_link(link_el):
    base_url = "https://annas-archive.org"
    return base_url + link_el

def parse_book_meta(book_meta_el):
    meta_text = book_meta_el.text.strip()
    parts = meta_text.split(", ")

    language = ""
    try:
        language = parts[0].split("[")[1].strip("]")
    except IndexError:
        pass
    book_type = parts[1]

    book_size = ""
    try:
        book_size = parts[2]
    except IndexError:
        pass

    book_size_mb = 0
    try:
        book_size_mb = float(book_size.split("MB")[0])
    except ValueError:
        pass

    return language, book_type, book_size_mb

def parse_publish_info(publish_info_el):
    publish_info = publish_info_el.text.strip()
    parts = publish_info.split(", ")

    publisher = parts[0]

    year = -1
    try:
        year = int(parts[-1])
    except ValueError:
        pass

    return publisher, year




def filter_books(books, ext, lang):
    if not ext and not lang:
        return books
    if not ext:
        return [book for book in books if book["language"] == lang]
    if not lang:
        return [book for book in books if book["book_type"] == ext]
    return [book for book in books if book["book_type"] == ext and book["language"] == lang]


def load_mam_requests_json():
    with open("mam_requests.json") as f:
        data = json.load(f)
        books = []
        for book in data:
            book_parsed = None
            try:
                book_parsed = parse_mam_request(book)
            except:
                print(f"Error parsing {book}")
            if book_parsed:
                books.append(book_parsed)
        return books



def parse_mam_request(mam_request):
    return {
        "title": mam_request["title"],
        "authors": [v for v in json.loads(mam_request["authors"]).values()],
    }


def search(providers=[], query=None, ext=None, lang=None, content=None):
    books = []
    for provider in providers:
        search_results = provider.search(query, ext, lang, content)
        books.extend(search_results)
    return books


def search_books(q=None, ext=None, lang=None, content=None):
    base_url = "https://annas-archive.org/search"
    url = f"{base_url}?q={q or ''}"
    url = urllib.parse.quote(url, safe=":/?=").replace("%26", "&")

    # print(f"Searching {url}")
    r = requests.get(url)
    html = remove_comments_from_html(r.text)
    soup = BeautifulSoup(html, "html.parser")

    books_el = soup.find_all("div", class_="h-[125]")
    books = [parse_book(book_el) for book_el in books_el]

    filtered_books = filter_books(books, ext, lang)

    return filtered_books



def similarity_percentage(book1, book2):
    """
    Computes the percentage of similarity between two book objects based on their attributes "title" and "authors".
    """
    # Get the set of authors for each book
    authors1 = set(book1["authors"])
    authors2 = set(book2["authors"])

    # Compute the Jaccard similarity coefficient for authors
    authors_similarity = len(authors1.intersection(authors2)) / len(authors1.union(authors2))

    # Compute the Levenshtein distance for titles
    title1 = book1["title"].lower()
    title2 = book2["title"].lower()
    n, m = len(title1), len(title2)
    if n > m:
        # Make sure n <= m, to use the smaller string as reference for computing similarity
        title1, title2 = title2, title1
        n, m = m, n
    distances = list(range(n+1))
    for j in range(1, m+1):
        previous_distance = distances[0]
        distances[0] = j
        for i in range(1, n+1):
            temp = distances[i]
            if title1[i-1] == title2[j-1]:
                distances[i] = previous_distance
            else:
                distances[i] = min(previous_distance, min(distances[i], distances[i-1])) + 1
            previous_distance = temp
    title_similarity = 1 - (distances[n] / max(n, m))

    # Compute the weighted average of similarities for each attribute
    similarity = authors_similarity * 0.4 + title_similarity * 0.6

    # Convert the similarity to a percentage and round to two decimal places
    percentage = round(similarity * 100, 2)

    return percentage


if __name__ == "__main__":
    mam_books = load_mam_requests_json()
    start = 200
    mam_books = mam_books[start:start+100]
    books_ok = []

    for index, mam_book in enumerate(mam_books):
        title = mam_book["title"]

        search_results = search_books(title)
        time.sleep(1)
        if not search_results:
            print(f"No results found for {title}")
            print()
            continue


        for result in search_results:
            percentage = similarity_percentage(mam_book, result)
            if percentage >= 80:
                books_ok.append({"mam_book": mam_book, "result": result, "percentage": percentage})

        print(f"Finished {index + 1}/{len(mam_books)}")


    for book in books_ok:
        print(f"Found {book['result']['title']} by {book['result']['authors']} with {book['percentage']}% similarity")
        print(f"Matching MAM book: {book['mam_book']['title']} by {book['mam_book']['authors']}")
        print(f"Link: {book['result']['link']}")
        webbrowser.open(book['result']['link'])
