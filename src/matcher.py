from difflib import SequenceMatcher
import math


class Matcher:

    def __init__(self, title_enabled=True, authors_enabled=True, release_year_enabled=True, language_enabled=True):
        self.title_enabled = title_enabled
        self.authors_enabled = authors_enabled
        self.release_year_enabled = release_year_enabled
        self.language_enabled = language_enabled

    def match(self, book, books, threshold=0.8):
        similarities = []

        for book2 in books:
            similarity = self.similarity(book, book2)
            similarities.append((book2, similarity))

        similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
        similarities = [similarity for similarity in similarities if similarity[1] >= threshold]
        return similarities

    def similarity(self, book1, book2):
        similarities = []

        similarity_title = self.similarity_title(book1, book2)
        similarities.append(similarity_title)

        similarity_authors = self.similarity_authors(book1, book2)
        similarities.append(similarity_authors)

        similarity_release_year = self.similarity_release_year(book1, book2)
        similarities.append(similarity_release_year)

        similarity_language = self.similarity_language(book1, book2)
        similarities.append(similarity_language)

        similarities = [similarity for similarity in similarities if similarity is not None]
        total = sum(similarities) / len(similarities)

        return total

    def similarity_title(self, book1, book2):
        if self.title_enabled and book1.title and book2.title:
            return SequenceMatcher(None, book1.title, book2.title).ratio()
        return None

    def similarity_authors(self, book1, book2):
        if self.authors_enabled and book1.authors and book2.authors:
            similarity = 0
            for author1 in book1.authors:
                for author2 in book2.authors:
                    similarity += SequenceMatcher(None, author1, author2).ratio()
            similarity /= len(book1.authors) * len(book2.authors)
            return similarity
        return None

    def similarity_release_year(self, book1, book2):
        if self.release_year_enabled and book1.release_year and book2.release_year:
            return self.gaussian(book1, book2)
        return None

    def gaussian(self, book1, book2):
        diff = abs(book1.release_year - book2.release_year)
        std_dev = 10
        mean = 0
        return math.exp(-((diff - mean) ** 2) / (2 * std_dev ** 2))

    def similarity_language(self, book1, book2):
        if self.language_enabled and book1.language and book2.language:
            return SequenceMatcher(None, book1.language, book2.language).ratio()
        return None
