from dataclasses import dataclass
import datetime as dt


@dataclass
class Book:
    title: str
    authors: list
    language: str
    release_year: int
    link: str

    def __post_init__(self):
        self.title = self.title.lower().strip() if self.title else None
        self.authors = [author.lower().strip() for author in self.authors] if self.authors else None
        self.language = self.language.lower().strip() if self.language else None
        self.release_year = int(self.release_year) if self.release_year else None
        self.link = self.link.strip() if self.link else None

    def __str__(self):
        return f"{self.title} by {self.authors} ({self.language})"

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get('title'),
            authors=data.get('authors'),
            language=data.get('language'),
            release_year=data.get('release_year'),
            link=data.get('link')
        )