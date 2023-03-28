from src.scraping.providers.pdfdrive import PdfDrive


if __name__ == "__main__":
    provider = PdfDrive()
    books = provider.search("the subtle art of not giving a fuck")
    print(books)
