class Scraper:

    def __init__(self, providers):
        self._providers = providers

    def search(self, query=None, ext=None, lang=None, content=None, pubyear=None):
        books = []
        for provider in self._providers:
            search_results = provider.search(query, ext, lang, content, pubyear)
            books.extend(search_results)
        return books
