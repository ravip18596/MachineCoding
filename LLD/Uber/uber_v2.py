"""
Enums - VehicleType, PaymentStatus, RideStatus, DriverStatus
Core entities - Rider, Driver, Location, PaymentReceipt, Trip
Strategy Design Pattern - FareStrategy (BaseFareStrategy, DynamicFareStrategy), PaymentStrategy (UPIPaymentStrategy), DriverMatchingStrategy
Facade Design Pattern - TripService
"""
import uuid
from typing import Dict
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto

class VehicleType(Enum):
    CAR = auto()
    BIKE = auto()
    AUTO = auto()

class PaymentStatus(Enum):
    SUCCESS = auto()
    FAIL = auto()

class RideStatus(Enum):
    REQUESTED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()

class DriverStatus(Enum):
    IDLE = auto()
    IN_RIDE = auto()


@dataclass
class Rider:
    id: int
    name: str
    home_address: str


@dataclass
class Driver:
    id: int
    name: str
    vehicle_type: VehicleType
    vehicle_number: str

@dataclass
class Location:
    distance: int
    lat: float
    lon: float
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

@dataclass
class PaymentReceipt:
    amount: float
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    payment_status: PaymentStatus = PaymentStatus.SUCCESS

@dataclass
class Trip:
    src: Location
    dest: Location
    rider: Rider
    driver: Driver
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    status: RideStatus = None


class FareStrategy(ABC):
    @abstractmethod
    def calculate_fare(self, trip: Trip, rate_card: Dict[VehicleType, int]) -> float: pass


class BaseFareStrategy(FareStrategy):
    def calculate_fare(self, trip, rate_card: Dict[VehicleType, int]) -> float:
        distance = abs(trip.src.distance - trip.dest.distance)
        print(f"[Base Fare Logic] distance = {distance}, rate: {rate_card[trip.driver.vehicle_type]}")
        amount = distance * rate_card[trip.driver.vehicle_type]
        return amount

@dataclass
class DynamicFareStrategy(FareStrategy):
    fare_multiplier: float = 1.5

    def calculate_fare(self, trip, rate_card: Dict[VehicleType, int]) -> float:
        distance = abs(trip.src.distance - trip.dest.distance)
        print(f"[Dynamic Fare Logic] distance = {distance}, rate: {rate_card[trip.driver.vehicle_type]*self.fare_multiplier}")
        amount = distance * rate_card[trip.driver.vehicle_type] * self.fare_multiplier
        return amount


class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount) -> PaymentReceipt:
        pass

@dataclass
class UPIPaymentStrategy(PaymentStrategy):
    vpa: str
    simulate_failure: bool = False
    def pay(self, amount) -> PaymentReceipt:
        print(f"[Payment Gateway] init payment of Rs {amount}")
        receipt = PaymentReceipt(amount=amount)
        if self.simulate_failure:
            receipt.payment_status = PaymentStatus.FAIL
        print(f"[Payment Gateway] payment of Rs {amount}. status = {receipt.payment_status}")
        return receipt


class TripService:
    def __init__(self, trip: Trip, fare_strategy: FareStrategy, payment_strategy: PaymentStrategy):
        self.trip = trip
        self.fare_strategy = fare_strategy
        self.payment_strategy = payment_strategy
        self.rate_card = {
            VehicleType.BIKE: 10,
            VehicleType.CAR: 20,
            VehicleType.AUTO: 30
        }

    def ride_requested(self):
        if self.trip.status is not None:
            raise Exception("[Trip Service] trip status is not None")
        print("[Trip Service] Status change to Requested")
        self.trip.status = RideStatus.REQUESTED

    def ride_in_progress(self):
        if self.trip.status != RideStatus.REQUESTED:
            raise Exception("[Trip Service] trip status is not REQUESTED")
        print("[Trip Service] Status change to IN_PROGRESS")
        self.trip.status = RideStatus.IN_PROGRESS

    def ride_completed(self) -> PaymentReceipt:
        if self.trip.status != RideStatus.IN_PROGRESS:
            raise Exception("[Trip Service] trip status is not IN_PROGRESS")
        print("[Trip Service] Status change to COMPLETED")
        self.trip.status = RideStatus.COMPLETED

        amount = self.fare_strategy.calculate_fare(self.trip, self.rate_card)
        receipt = self.payment_strategy.pay(amount)
        return receipt


if __name__ == '__main__':
    trip = Trip(
        src=Location(distance=10, lat=26.45, lon=23.21),
        dest = Location(distance=25, lat=26.15, lon=24.21),
        rider=Rider(id=1, name="Ravi", home_address="a1"),
        driver=Driver(id=1, name="Prakash", vehicle_type=VehicleType.CAR, vehicle_number="DL9CBB5204")
    )

    upi_payment = UPIPaymentStrategy(vpa="abc@ybl")
    fare_strategy = DynamicFareStrategy()
    trip_service = TripService(trip=trip, fare_strategy=fare_strategy, payment_strategy=upi_payment)

    trip_service.ride_requested()
    trip_service.ride_in_progress()
    receipt = trip_service.ride_completed()

    print(f"[main] Payment Receipt: {receipt}")