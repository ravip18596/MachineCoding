"""
Requirements:
1. Design multi level parking lot
2. Support for multiple types of vehicles
3. Prevent concurrent parking of different vehicles
4. Payment and booking of parking slots will be supported
"""
import random
import threading
from enum import Enum, auto
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import uuid
from collections import defaultdict
from typing import Dict, List, Optional, Union


class VehicleType(Enum):
    TWO_WHEELER = auto()
    FOUR_WHEELER = auto()


@dataclass
class ParkingSlot:
    id: int
    expire_at: float
    vehicle_no: Optional[str] = 'empty'
    vehicle_type: Optional['VehicleType'] = VehicleType.FOUR_WHEELER

    def __str__(self) -> str:
        return f"id: {self.id}, expire_at: {self.expire_at}, vehicle_no:{self.vehicle_no}, vehicle_type: {self.vehicle_type}"


@dataclass
class ParkingFloor:
    id: int
    slot_map: Dict[int, ParkingSlot] = field(default_factory=lambda: defaultdict(ParkingLot))

@dataclass
class ParkingLot:
    floor_map: Dict[int, ParkingFloor] = field(default_factory=lambda: defaultdict(ParkingFloor))

class PaymentStatus(Enum):
    SUCCESS = auto()
    FAIL = auto()

class ParkingRate(Enum):
    TWO_WHEELER = 30
    FOUR_WHEELER = 50

@dataclass
class PaymentReceipt:
    txn_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    amt: float = 0.0

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amt: float) -> PaymentReceipt:
        pass

@dataclass
class CreditCardPaymentStrategy(PaymentStrategy):
    cc_no: str

    def pay(self, amt: float) -> PaymentReceipt:
        return PaymentReceipt(amt=amt)

@dataclass
class UPIPaymentStrategy(PaymentStrategy):
    vpa: str

    def pay(self, amt: float) -> PaymentReceipt:
        return PaymentReceipt(amt=amt)

# Facade Design Pattern
# adding veil in back becoming interface
class SlotBookingService:
    def __init__(self, parking_lot: ParkingLot, payment_strategy: PaymentStrategy):
        self.parking_lot = parking_lot
        self.payment_strategy = payment_strategy
        self._lock = threading.RLock()

    def book_slot(self, vehicle_no: str , vehicle_type: VehicleType, floor_no: int) -> Union[ParkingSlot, PaymentReceipt]:
        with self._lock:
            if floor_no not in self.parking_lot.floor_map:
                raise ValueError(f"Incorrect floor no: {floor_no} provided")

            # map of all slots in particular floor
            floor_slot_map = self.parking_lot.floor_map[floor_no]
            assigned_parking_slot = None
            # add check to see if all slots are full or not
            for id, parking_slot in floor_slot_map.slot_map.items():
                map = floor_slot_map.slot_map[id]
                if map.vehicle_no not in ['empty', vehicle_no]:
                    continue

                floor_slot_map.slot_map[id].vehicle_no = vehicle_no
                floor_slot_map.slot_map[id].vehicle_type = vehicle_type
                assigned_parking_slot = floor_slot_map.slot_map[id]
                break

            amt = ParkingRate.FOUR_WHEELER if vehicle_type == VehicleType.FOUR_WHEELER else ParkingRate.TWO_WHEELER
            payment_receipt = self.payment_strategy.pay(amt=amt)

            return assigned_parking_slot, payment_receipt

if __name__ == "__main__":
    # init
    num_slots = 100 # per floor
    slots = []
    for i in range(num_slots):
        if i<=num_slots//2:
            parking_slot = ParkingSlot(id=i, vehicle_type=VehicleType.TWO_WHEELER, expire_at=3600)
            slots.append(parking_slot)
        else:
            parking_slot = ParkingSlot(id=i, vehicle_type=VehicleType.FOUR_WHEELER, expire_at=3600)
            slots.append(parking_slot)

    num_floors = 4
    parking_lot = ParkingLot()
    for i in range(num_floors):
        parking_floor = ParkingFloor(id=i)
        for slot in slots:
            parking_floor.slot_map[slot.id] = slot

        parking_lot.floor_map[i] = parking_floor

    cc_pay = CreditCardPaymentStrategy(cc_no="abc123")
    upi_pay = UPIPaymentStrategy(vpa="abc@ptsbi")

    slot_booking_service = SlotBookingService(parking_lot=parking_lot, payment_strategy=cc_pay)

    assigned_parking_slot, payment_receipt = slot_booking_service.book_slot(vehicle_no="DL9CBB5204", vehicle_type=VehicleType.FOUR_WHEELER, floor_no=1)
    print(f'Payment Receipt generated - {payment_receipt}')
    print(f"Parking slot assigned - ", assigned_parking_slot )
    assigned_parking_slot = slot_booking_service.book_slot(vehicle_no="DL9SAB4567", vehicle_type=VehicleType.TWO_WHEELER, floor_no=3)
    print(f'Payment Receipt generated - {payment_receipt}')
    print(f"Parking slot assigned - ", assigned_parking_slot)

