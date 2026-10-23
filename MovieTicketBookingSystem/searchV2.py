from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional

# ==========================================
# 1. Enums
# ==========================================
class Language(Enum):
    ENGLISH = auto()
    HINDI = auto()
    MALYALAM = auto()

class Genre(Enum):
    ACTION = auto()
    THRILLER = auto()
    FICTION = auto()

class City(Enum):
    DELHI = auto()
    MUMBAI = auto()
    KOLKATA = auto()
    CHENNAI = auto()

# ==========================================
# 2. Domain Entities
# ==========================================
@dataclass(frozen=True)
class Movie:
    id: str
    title: str
    description: str
    genre: Genre
    language: Language


@dataclass(frozen=True)
class Show:
    id: str
    cinema_hall: str
    movie: Movie


# ==========================================
# 3. Catalog with Adjacency List
# ==========================================
class MovieCatalog:
    def __init__(self) -> None:
        self._city_wise_shows: Dict[City, List[Show]] = defaultdict(list)

    def add_shows(self, city:City, show: Show):
        self._city_wise_shows[city].append(show)

    def search_movies(self, city: City, genre: Optional[Genre] = None, language: Optional[Language] = None) -> List[Movie]:
        unique_movies = {}
        for show in self._city_wise_shows[city]:
            movie = show.movie
            if genre is not None and movie.genre != genre:
                continue
            if language is not None and movie.language != language:
                continue

            unique_movies[movie.id] = movie

        return list(unique_movies.values())
        

if __name__ == '__main__':
    m1 = Movie(id="m1", title='Awarapan2',description="Action", genre=Genre.ACTION, language=Language.HINDI)
    m2 = Movie(id="m2", title='Drishyam3',description="Thriller", genre=Genre.THRILLER, language=Language.HINDI)
    m3 = Movie(id="m3", title='The Dark Knight',description="Fiction", genre=Genre.FICTION, language=Language.ENGLISH)

    catalog = MovieCatalog()
    catalog.add_shows(city=City.DELHI, show=Show(id="s1", cinema_hall="PVR Inox Saket", movie=m1))
    catalog.add_shows(city=City.DELHI, show=Show(id="s2", cinema_hall="PVR Inox Dwarka", movie=m2))
    catalog.add_shows(city=City.MUMBAI, show=Show(id="s3", cinema_hall="PVR Inox Nariman", movie=m3))

    # Show movies running in Delhi
    movies = catalog.search_movies(city=City.DELHI)
    for movie in movies:
        print(f"Movie running in Delhi: {movie.title}")

    # Show movies running in Mumbai having genre fiction
    movies = catalog.search_movies(city=City.MUMBAI, genre=Genre.FICTION)
    for movie in movies:
        print(f"Movie running in Mumbai having genre fiction: {movie.title}")
