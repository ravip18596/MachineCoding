"""
## Problem Prompt
Design the Low-Level Design (LLD) for a Ride-Sharing System (like Uber/Lyft) supporting riders requesting trips,
drivers accepting/completing trips, dynamic fare calculation, and concurrent driver matching.
Outline the core classes, interfaces/design patterns, state transitions, and thread-safe matching logic.
"""

import uuid
from typing import List
from enum import Enum, auto
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


class VehicleType(Enum):
    BIKE = auto()
    AUTO = auto()
    CAR = auto()


class TripStatus(Enum):
    STALE = auto()
    REQUESTED = auto()
    ACCEPTED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    CANCELLED = auto()

@dataclass
class User:
    user_id: int
    name: str
    address: str
    contact_no: str
    otp: int


@dataclass
class Driver:
    driver_id: int
    name: str
    vehicle_no: str
    vehicle_type: VehicleType


@dataclass
class Location:
    lat: float
    lon: float
    distance: float
    location_id: str = field(default_factory=lambda: uuid.uuid4().hex)


@dataclass
class Review:
    rating: int
    review_id: str = field(default_factory=lambda: uuid.uuid4().hex)


@dataclass
class Trip:
    src: Location
    dest: Location
    user_id: int
    driver_id: int
    trip_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    status: TripStatus = TripStatus.STALE

class FareStrategy(ABC):
    @abstractmethod
    def calculate_fare(self, src, dest: Location, vehicle_type: VehicleType) -> float: pass

@dataclass
class BasePricingStrategy(FareStrategy):
    base_fare: dict

    def calculate_fare(self, src, dest: Location, vehicle_type: VehicleType) -> float:
        distance = abs(src.distance - dest.distance)
        return distance * self.base_fare[vehicle_type]


class SurgePricingStrategy(FareStrategy):
    def __init__(self, base_price: dict, surge_pricing_multiplier: float = 1.5):
        self.base_price = base_price
        self.surge_multiplier = surge_pricing_multiplier

    def calculate_fare(self, src, dest: Location, vehicle_type: VehicleType) -> float:
        distance = abs(src.distance - dest.distance)
        return distance * self.base_price[vehicle_type] * self.surge_multiplier


class PaymentStatus(Enum):
    FAIL = auto()
    SUCCESS = auto()
    REFUND_FAIL = auto()
    REFUND_PASS = auto()

@dataclass
class PaymentReceipt:
    amount: float
    user_id: int
    txn_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    payment_status: PaymentStatus = PaymentStatus.SUCCESS


class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount, user_id) -> PaymentReceipt:
        pass

    @abstractmethod
    def refund(self, amount, user_id) -> PaymentReceipt:
        pass


@dataclass
class UPIPaymentStrategy(PaymentStrategy):
    vpa: str
    simulate_failure: bool = False

    def pay(self, amount: float, user_id: int) -> PaymentReceipt:
        print(f"[Payment Gateway] Ride fare calculated of: Rs {amount} ")
        payment_receipt = PaymentReceipt(amount, user_id=user_id)
        if self.simulate_failure:
            payment_receipt.payment_status = PaymentStatus.FAIL
            print(f"[Payment Gateway] Fare deduction from UPI address: {self.vpa} of amount Rs.{amount} failed")
        else:
            print(f"[Payment Gateway] Fare deduction from UPI address: {self.vpa} of amount Rs.{amount} succeeded")
        return payment_receipt

    def refund(self, amount: float, user_id: int) -> PaymentReceipt:
        print(f"[Payment Gateway] Ride fare refund calculated of: Rs {amount} ")
        payment_receipt = PaymentReceipt(amount, user_id=user_id, payment_status=PaymentStatus.REFUND_PASS)
        if self.simulate_failure:
            payment_receipt.payment_status = PaymentStatus.REFUND_FAIL
            print(f"[Payment Gateway] Fare refund to UPI address: {self.vpa} of amount Rs.{amount} failed")
        else:
            print(f"[Payment Gateway] Fare refund to UPI address: {self.vpa} of amount Rs.{amount} succeeded")
        return payment_receipt


class TripManager:
    def __init__(self, users: List[User], drivers: List[Driver], payment_strategy: PaymentStrategy, fare_strategy: FareStrategy):
        self.payment_strategy = payment_strategy
        self.fare_strategy = fare_strategy
        self.user_map = {}
        self.driver_map = {}
        for user in users:
            self.user_map[user.user_id] = user

        for driver in drivers:
            self.driver_map[driver.driver_id] = driver


    def request_trip(self, trip: Trip):
        trip.status = TripStatus.REQUESTED

    def accept_trip(self, trip: Trip):
        trip.status = TripStatus.ACCEPTED

    def start_trip(self, trip: Trip):
        trip.status = TripStatus.IN_PROGRESS

    def complete_trip(self, trip: Trip) -> PaymentReceipt:
        trip.status = TripStatus.COMPLETED
        driver = self.driver_map[trip.driver_id]
        amt = self.fare_strategy.calculate_fare(trip.src, trip.dest, driver.vehicle_type)
        payment_receipt = self.payment_strategy.pay(amount=amt, user_id=trip.user_id)
        return payment_receipt

    def cancel_trip(self, trip: Trip):
        trip.status = TripStatus.CANCELLED


if __name__ == '__main__':
    users = [
        User(user_id=1, name="Ravi", address="a1", otp=1234, contact_no="+91-12345678"),
        User(user_id=2, name="Ra", address="a2", otp=1235, contact_no="+91-12345678"),
        User(user_id=3, name="R", address="a3", otp=1236, contact_no="+91-7891278789")
    ]
    drivers = [
        Driver(driver_id=1, name="Prakash", vehicle_no="DL9CBB5204", vehicle_type=VehicleType.CAR),
        Driver(driver_id=2, name="Pra", vehicle_no="DL4CDH9878", vehicle_type=VehicleType.AUTO),
        Driver(driver_id=3, name="P", vehicle_no="DL9CGG5204", vehicle_type=VehicleType.BIKE),
    ]
    src = Location(lat=28.56, lon=30.76, distance=10)
    dest = Location(lat=27.56, lon=29.76, distance=30)

    base_price = {
        VehicleType.CAR: 30,
        VehicleType.AUTO: 20,
        VehicleType.BIKE: 10,
    }
    upi_payment_strategy = UPIPaymentStrategy(vpa="ravi@ybl")
    surge_fare_strategy = SurgePricingStrategy(base_price=base_price)

    trip_manager = TripManager(users, drivers, upi_payment_strategy, surge_fare_strategy)
    trip = Trip(user_id=1, driver_id=1, src=src, dest=dest)
    trip_manager.request_trip(trip)
    trip_manager.accept_trip(trip)
    trip_manager.start_trip(trip)
    payment_receipt = trip_manager.complete_trip(trip)
    print(f"Trip successful. Here is the payment receipt: {payment_receipt}")