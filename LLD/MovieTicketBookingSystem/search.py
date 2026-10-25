from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Set, Dict
from abc import abstractmethod, ABC
from threading import RLock
# Movie is tied to a show screened in a cinemahall located in a city.

# 1. value objects and enums
class Genre(Enum):
    ACTION = auto()
    THRILLER = auto()
    COMEDY = auto()

class Language(Enum):
    HINDI = auto()
    ENGLISH = auto()
    MALAYALAM = auto()

@dataclass(frozen=True)
class City:
    id: str
    name: str

# 2. Core domain entites
@dataclass(frozen=True)
class Movie:
    id: str
    title: str
    description: str
    genres: Set[Genre]
    languages: Set[Language]

@dataclass
class Show:
    id: str
    start_time: datetime
    end_time: datetime
    movie_id: str
    cinema_hall_id: str

@dataclass
class CinemaHall:
    id: str
    name: str
    city_id: str
    shows: List[Show] = field(default_factory=list)

############################################################
# Specification Design Pattern - encapsulate search criteria
# ABC and abstract method defines a class contract
############################################################

class MovieSearchCriteria(ABC):
    @abstractmethod
    def is_matching(self, movie:Movie) -> bool:
        pass

class GenreSearchCriteria(MovieSearchCriteria):
    def __init__(self, genre: Genre):
        self.genre = genre

    def is_matching(self, movie: Movie) -> bool:
        return self.genre in movie.genres


class LanguageSearchCriteria(MovieSearchCriteria):
    def __init__(self, language: Language) -> None:
        self.language = language

    def is_matching(self, movie: Movie) -> bool:
        return self.language in movie.languages


class AndSearchCriteria(MovieSearchCriteria):
    def __init__(self, *specs: MovieSearchCriteria) -> None:
        # *specs will be list of future search criterias
        self.specs = specs

    def is_matching(self, movie: Movie) -> bool:
        return all(spec.is_matching(movie) for spec in self.specs)


# ==========================================
# 4. Repository Contract & In-Memory Store
#    Repository Design Pattern
# ==========================================
class MovieCatalogRepository(ABC):
    @abstractmethod
    def get_movie_by_city(self, city: str) -> List[Movie]:
        pass

    @abstractmethod
    def get_movie_by_id(self, id: str) -> Optional[Movie]:
        pass

class InMemoryMovieCatalogRepo(MovieCatalogRepository):
    # Maintain an inverted index City -> Set[Movie]
    # Thread safe implementation
    def __init__(self) -> None:
        self._movies: Dict[str, Movie] = {}
        self._cinema_hall: Dict[str, CinemaHall] = {}
        # reverse index City_id to Set[Movie]
        self._city_to_movie_idx: Dict[str, Set[str]] = {}
        # Lock init
        self._lock = RLock()

    def add_movie(self, movie: Movie) -> None:
        with self._lock:
            self._movies[movie.id] = movie

    def register_show(self, cinema_hall: CinemaHall, show: Show):
        with self._lock:
            self._cinema_hall[cinema_hall.id] = cinema_hall
            cinema_hall.shows.append(show)

    def get_movie_by_city(self, city_id: str) -> List[Movie]:
        pass
    
    def get_movie_by_id(self, movie_id: str) -> Movie | None:
        pass


class MovieSearchService(MovieCatalogRepository):
    def list_movies_by_city(city_id: str, spec):
        pass


if __name__ == '__main__':
    delhi = City(id="DEL", name='Delhi')
    mumbai = City(id="BOM", name="Mumbai")

    m1 = Movie(id="M1", title="Awarapan", description="Action", genres={Genre.ACTION}, languages={Language.ENGLISH})
    m2 = Movie(id="M2", title="Drisyam", description="Thriller", genres={Genre.THRILLER}, languages={Language.HINDI, Language.MALAYALAM})
    m3 = Movie(id="M3", title="Phir Hera Pheri", description="Comedy", genres={Genre.COMEDY}, languages={Language.HINDI})

    repo = InMemoryMovieCatalogRepo()
    repo.add_movie(m1)
    repo.add_movie(m2)
    repo.add_movie(m3)

    # 2. Setup cinema hall and shows
    pvr_delhi = CinemaHall(id="pvr_delhi", name="PVR Delhi",  city_id=delhi.id)
    pvr_mumbai = CinemaHall(id="pvr_mumbai", name="PVR Mumbai", city_id=mumbai.id)

    show1 = Show(id="s1", start_time=datetime.now(), end_time=datetime.now(), movie_id=m1.id, cinema_hall_id=pvr_delhi.id)
    show2 = Show(id="s2", start_time=datetime.now(), end_time=datetime.now(), movie_id=m2.id, cinema_hall_id=pvr_mumbai.id)
    show3 = Show(id="s3", start_time=datetime.now(), end_time=datetime.now(), movie_id=m1.id, cinema_hall_id=pvr_mumbai.id)

    repo.register_show(pvr_delhi, show=show1)
    repo.register_show(pvr_mumbai, show=show2)
    repo.register_show(pvr_mumbai, show=show3)

    # 3. Query Service
    service = MovieSearchService(movie_catalog_repo=repo)

    # 3.1 Search all movies running in city Delhi
    delhi_movies = service.list_movies_by_city(delhi.id)
    for movie in delhi_movies:
        print(movie)

    # 3.2 Search movie by Hindi lang and Comedy genre

    spec_criteria = AndSearchCriteria(GenreSearchCriteria(genre=Genre.COMEDY), LanguageSearchCriteria(language=Language.HINDI))
    delhi_hindi_comedy_movie = service.list_movies_by_city(delhi.id, spec=spec_criteria)
    for movie in delhi_hindi_comedy_movie:
        print(movie)






