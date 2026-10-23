from collections import defaultdict
from random import randrange
from typing import List


# A movie is tied to a show screened in a hall inside a theatre located in a city

class Movie:
    def __init__(self, movie_name, movie_description, movie_genre) -> None:
        self.movie_name = movie_name
        self.movie_description = movie_description
        self.movie_genre = movie_genre

    def __str__(self) -> str:
        return f"Movie Name: {self.movie_name}, Description: {self.movie_description}, Movie Genre: {self.movie_genre}"


def search_movie_by_city(city: str, city_wise_search_map: dict) -> List[Movie]:
    movies = city_wise_search_map[city]
    return movies


if __name__ == '__main__':
    active_cities = ['Delhi','Mumbai','Kolkata', 'Chennai']
    # init movies
    movies = [  Movie('Awarapan1', 'description1', 'genre1'),   
                    Movie('Awarapan2', 'description2', 'genre2'),
                    Movie('Drishyam3', 'description3', 'genre3') ]

    # city wise adjacency list 
    city_wise_search_map = defaultdict(set)
    for city in active_cities:
        for _ in range(2):
            city_wise_search_map[city].add(movies[randrange(3)])

    # search movie by city
    for city in active_cities:
        movies = search_movie_by_city(city, city_wise_search_map)
        print(city)
        for movie in movies:
            print(movie)

    



