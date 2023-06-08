from enum import Enum
from datetime import datetime
from typing import List

class BookingStatus(Enum):
    REQUESTED, PENDING, CONFIRMED, CANCELLED = 1, 2, 3, 4

class PaymentStatus(Enum):
    PENDING, SUCCESS, CONFIRMED, REFUNDED = 1, 2, 3, 4

class AccountStatus(Enum):
    ACTIVE, INACTIVE, BLOCKED, CLOSED = 1, 2, 3, 4

class SeatType(Enum):
    PREMIUM, REGULAR, EMERGENCY_EXIT = 1, 2, 3


class Address:
    def __init__(self, street, city, state, zip_code, country) -> None:
        self.__street_address = street
        self.__city = city
        self.__state = state
        self.__zip_code = zip_code
        self.__country = country

'''
Account, Customer, Guest, Admin, FrontDesk - These classes represent the different people that
 interact with our system:
'''

class Account:
    def __init__(self, id, password, status=AccountStatus.ACTIVE):
        self.__id = id
        self.__password = password
        self.__status = status

    def reset_password(self):
        None

from abc import ABC, abstractmethod

class Person(ABC):
    def __init__(self, name, address:Address, email, phone, account) -> None:
        self.__name = name
        self.__address = address
        self.__email = email
        self.__phone = phone
        self.__account = account

class Customer:
    def create_booking(self, booking: Booking):
        pass

    def get_bookings():
        pass


class FrontDesk:
    def create_booking(self, booking: Booking):
        pass

class Admin:
    def add_movie(self, movie):
        pass

    def add_show(self, show):
        pass

    def block_customer(self, customer):
        pass


class Guest:
    def register_account(self):
        pass


''' 
A movie has many shows
'''
class Show:
    def __init__(self, id, movie: Movie, start_time, end_time, played_at: CinemaHall) -> None:
        self.__show_id = id
        self.__movie = movie
        self.__start_time = start_time
        self.__end_time = end_time
        self.__played_at = played_at

class Movie:
    def __init__(self, title, genre, desc, country, duration_in_mins, lang, rel_date, added_by: Admin) -> None:
        self.__title = title
        self.__genre = genre
        self.__description = desc
        self.__country = country
        self.__duration_in_mins = duration_in_mins
        self.__language = lang
        self.__release_date = rel_date
        self.__added_by = added_by

        self.__shows = []

    def get_shows() -> List(Show):
        return 


'''
Customers reserve seats using booking and make payments
'''

class Booking:
    def __init__(self, booking_no, show_id, status: BookingStatus, show_seats: ShowSeat, num_seats, payment) -> None:
        self.__booking_number = booking_no
        self.__show = show_id
        self.__status = status
        self.__seats = show_seats
        self.__created_on = datetime.now()
        self.__num_seats = num_seats
        self.__payment = payment

    def cancel(self):
        pass

    def make_payment(self, payment):
        pass

    def assign_seats(self, seats):
        pass


class ShowSeat:
    def __init__(self, id: int, is_reserved: bool, price) -> None:
        self.__seat_id = id
        self.is_reserved = is_reserved
        self.price = price

class Payment:
    def __init__(self, amt, txn_id, status) -> None:
        self.__amount = amt
        self.__created_on = datetime.now()
        self.__transaction_id = txn_id
        self.__payment_status = status

'''
Each city has many cinemas and each cinema has many cinemaHalls
'''

class City:
    def __init__(self, name, state, zip_code) -> None:
        self.__name = name
        self.__state = state
        self.zip_code = zip_code

class Cinemas:
    def __init__(self, name: str, location, total_cinema_halls, halls: CinemaHall) -> None:
        self.__name = name
        self.__address = location
        self.__total_cinema_halls = total_cinema_halls
        self.__halls = halls

class CinemaHall:
    def __init__(self, name, total_seats, seats: ShowSeat, shows: Show) -> None:
        self.__name = name
        self.__total_seats = total_seats
        self.__seats = seats
        self.__shows = shows

'''
Catalog will implement Search to facilitate product search
'''

class Search(ABC):
    def search_by_title(self, title):
        pass

    def search_by_genre(self, genre):
        pass

    def search_by_release_date(self, release_date):
        pass

    def search_by_language(self, lang):
        pass

    def search_by_city(self, city):
        pass


class Catalog(Search):
    def __init__(self) -> None:
        self.__movie_titles = {}
        self.__movie_genres = {}
        self.__movie_langs = {}
        self.__movie_rel_date = {}
        self.__movie_cities = {}

    def search_by_city(self, city):
        return self.__movie_cities.get(city)
    
    def search_by_title(self, title):
        return self.__movie_titles.get(title)
    
    def search_by_lang(self, lang):
        return self.__movie_langs.get(lang)
    
    def search_by_genres(self, genre):
        return self.__movie_genres.get(genre)
    
    def search_by_release_date(self, rel_date):
        return self.__movie_rel_date.get(rel_date)
    

