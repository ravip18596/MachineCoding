"""
Core Entities => CinemaHall, Screen, Show, Seat, Movie, PaymentReceipt
Enums => Langauge, Genre, PaymentStatus
Strategy DP => PaymentStrategy
Facade DP => SeatBookingService

"""
import threading
import time
import uuid
from enum import Enum, auto
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class Langauge(Enum):
    ENGLISH = auto()
    HINDI = auto()
    MALAYALAM = auto()

class Genre(Enum):
    THRILLER = auto()
    COMEDY = auto()
    FICTION = auto()

class PaymentStatus(Enum):
    SUCCESS = auto()
    FAIL = auto()
    REFUND_SUCCESS = auto()
    REFUND_FAIL = auto()

class SeatStatus(Enum):
     AVAILABLE = auto()
     HOLD = auto()
     BOOKED = auto()

@dataclass
class CinemaHall:
    screens: List[int]
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

@dataclass
class Screen:
    show_ids: List[int]
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

@dataclass
class Movie:
    id: int
    name: str
    language: Langauge
    genre: Genre

@dataclass
class Show:
    seat_ids: List[int]
    id: int
    movie: Movie

@dataclass
class User:
    name: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

@dataclass
class Seat:
    id: int
    amount: float
    seat_status: SeatStatus = SeatStatus.AVAILABLE
    locked_by: Optional[User] = None
    hold_secs: int = 2
    expires_at: float = float('inf')

    def is_available(self) -> bool:
        return self.seat_status == SeatStatus.AVAILABLE or (self.seat_status == SeatStatus.HOLD and time.time() >= self.expires_at)

    def hold_seats(self, user: User):
        if self.seat_status != SeatStatus.AVAILABLE:
            raise ValueError("[Seat] seat status is not available")
        now = time.time()
        self.locked_by = user
        self.expires_at = now + self.hold_secs
        self.seat_status = SeatStatus.HOLD

    def book_seat(self, user: User):
        if self.seat_status != SeatStatus.HOLD:
            raise ValueError("[Seat] seat status is not hold")
        if self.locked_by == user and time.time() < self.expires_at:
            self.seat_status = SeatStatus.BOOKED

    def release_seat(self):
        if self.seat_status != SeatStatus.BOOKED:
            raise ValueError("[Seat] seat status is not booked")
        self.locked_by = None
        self.expires_at = float('inf')
        print(f"Successfully released hold on seat id: {self.id}")
        self.seat_status = SeatStatus.AVAILABLE


@dataclass
class PaymentReceipt:
    amount: float
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    status: PaymentStatus = PaymentStatus.SUCCESS


class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> PaymentReceipt:pass
    @abstractmethod
    def refund(self, amount: float) -> PaymentReceipt: pass

@dataclass
class UPIPayment(PaymentStrategy):
    vpa: str
    simulate_failure: bool = False

    def pay(self, amount) -> PaymentReceipt:
        receipt = PaymentReceipt(amount=amount)
        if self.simulate_failure:
            receipt.status = PaymentStatus.FAIL
            print(f"[PG] Payment of amount: {amount} failed for vpa: {self.vpa}")
        else:
            print(f"[PG] Payment of amount: {amount} successful for vpa: {self.vpa}")
        return receipt

    def refund(self, amount) -> PaymentReceipt:
        receipt = PaymentReceipt(amount=amount, status=PaymentStatus.REFUND_SUCCESS)
        if self.simulate_failure:
            receipt.status = PaymentStatus.REFUND_FAIL
            print(f"[PG] Refund of amount: {amount} failed for vpa: {self.vpa}")
        else:
            print(f"[PG] Refund of amount: {amount} successful for vpa: {self.vpa}")
        return receipt


class BookingService:
    def __init__(self, seat_amount_map: Dict[int, int], pay_strategy: PaymentStrategy):
        self.seats = [Seat(id=id, amount=amt) for id, amt in seat_amount_map.items()]
        self.pay_strategy = pay_strategy
        self._lock = threading.Lock()

    def _fetch_seat(self, seat_id) -> Seat:
        seat = None
        for s in self.seats:
            if s.id == seat_id:
                seat = s
        if seat is None:
            raise ValueError("incorrect seat no provided")
        return seat

    def book_seat(self, user: User, seat_id: int):
        with self._lock:
            seat = self._fetch_seat(seat_id)
            if not seat.is_available():
                raise ValueError("[Service] Requested seat is not available")

            seat.hold_seats(user=user)

        receipt = self.pay_strategy.pay(seat.amount)
        if receipt.status == PaymentStatus.SUCCESS:
            print(f"Payment is successful. Receipt: {receipt}")
            with self._lock:
                seat.book_seat(user)
        else:
            print(f"Payment is unsuccessful. Proceeding to refund.")
            with self._lock:
                seat.release_seat()
            receipt = self.pay_strategy.refund(seat.amount)
            print(f"[Service] refund receipt: {receipt}")

    def cancel_seat_booking(self, seat_id: int):
        with self._lock:
            seat = self._fetch_seat(seat_id)
            if seat.is_available():
                print("no need to cancel seat booking")
                return

            seat.release_seat()
            print(f"[Service] Seat:{seat_id} booking cancelled")

        receipt = self.pay_strategy.refund(seat.amount)
        print(f"[Service] refund receipt: {receipt}")


if __name__ == '__main__':
    user1 = User(name="Ravi Prakash")
    upi_pay_strategy = UPIPayment(vpa="abc@ybl")
    seat_amount_map = {
        1: 100,
        2: 200,
        3: 300
    }
    movie = Movie(id=1, name="Drishyam", language=Langauge.HINDI, genre=Genre.THRILLER)
    show = Show(id=1, seat_ids=[1,2,3], movie=movie)
    screen = Screen(show_ids=[1])
    cinema_hall = CinemaHall(screens=[1])

    service = BookingService(seat_amount_map, pay_strategy=upi_pay_strategy)
    service.book_seat(user1, seat_id=1)
    print()
    service.cancel_seat_booking(seat_id=1)
