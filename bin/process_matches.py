import json
import webbrowser

from src.book import Book


if __name__ == "__main__":
    match_filepath = "out/matches.json"
    with open(match_filepath, 'r') as f:
        matches = json.load(f)

    for match in matches:
        mam_book = Book.from_dict(match[0])
        print(f"MAM book: {mam_book.title}")

        matches = sorted(match[1], key=lambda x: x[1], reverse=True)
        for match in matches:
            book = Book.from_dict(match[0])
            print(f"Link: {book.link} - {match[1]:.2f}")
            webbrowser.open(book.link)

        input("Press enter to continue...")
        print()
