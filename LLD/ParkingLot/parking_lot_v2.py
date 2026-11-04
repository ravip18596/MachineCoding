"""
Requirements:
1. Design multi level parking lot
2. Support for multiple types of vehicles
3. Prevent concurrent parking of different vehicles
4. Payment and booking of parking slots will be supported
"""
import time
import threading
from enum import Enum, auto
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import uuid
from typing import Dict, Set, Optional, Union, Tuple


class VehicleType(Enum):
    TWO_WHEELER = auto()
    FOUR_WHEELER = auto()


@dataclass
class ParkingSlot:
    id: int
    expire_at: float
    vehicle_no: str = 'empty'
    vehicle_type: Optional['VehicleType'] = None

    def __str__(self) -> str:
        return f"id: {self.id}, expire_at: {self.expire_at}, vehicle_no:{self.vehicle_no}, vehicle_type: {self.vehicle_type}"


@dataclass
class ParkingFloor:
    id: int
    slot_map: Dict[int, ParkingSlot] = field(default_factory=dict)
    available_2w_ids: Set[int] = field(default_factory=set)
    available_4w_ids: Set[int] = field(default_factory=set)
    """
    Moving to Granular locking.
    - We will apply lock per floor basis. This will prevent blocking other vehicle to access other floors.
    - this will avoid global lock and support multiple entry and exit per parking lot
    """
    lock: threading.RLock = field(default_factory=threading.RLock)  # lock per instance

@dataclass
class ParkingLot:
    floor_map: Dict[int, ParkingFloor] = field(default_factory=dict)

class PaymentStatus(Enum):
    SUCCESS = auto()
    FAIL = auto()

class ParkingRate(Enum):
    TWO_WHEELER = 30
    FOUR_WHEELER = 50

@dataclass
class PaymentReceipt:
    status: PaymentStatus
    txn_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    amt: float = 0.0

# Strategy Pattern
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amt: float) -> PaymentReceipt:
        pass

@dataclass
class CreditCardPaymentStrategy(PaymentStrategy):
    cc_no: str
    simulate_failure: bool = False

    def pay(self, amt: float) -> PaymentReceipt:
        if self.simulate_failure:
            return PaymentReceipt(amt=amt, status=PaymentStatus.FAIL)

        return PaymentReceipt(amt=amt, status=PaymentStatus.SUCCESS)

@dataclass
class UPIPaymentStrategy(PaymentStrategy):
    vpa: str

    def pay(self, amt: float) -> PaymentReceipt:
        return PaymentReceipt(amt=amt, status=PaymentStatus.SUCCESS)

# Facade Design Pattern
# provides veil in back becoming an interface
class SlotBookingService:
    def __init__(self, parking_lot: ParkingLot, payment_strategy: PaymentStrategy, default_parking_time: int):
        self.parking_lot = parking_lot
        self.payment_strategy = payment_strategy

        self.default_parking_time = default_parking_time

    def book_slot_v2(self, vehicle_no: str, vehicle_type: VehicleType, floor_no: int) -> Tuple[ParkingSlot, PaymentReceipt]:
        if floor_no not in self.parking_lot.floor_map:
            raise ValueError(f"Incorrect {floor_no} provided")
        floor = self.parking_lot.floor_map[floor_no]
        now = time.time()
        # 1. Acquire Floor Lock to assign slot in O(1)
        with floor.lock:
            target_set = floor.available_2w_ids
            if vehicle_type == VehicleType.FOUR_WHEELER:
                target_set = floor.available_4w_ids

            # assign new block
            assigned_slot_id = target_set.pop()
            if assigned_slot_id is None:
                raise ValueError("No available slots")
            floor.slot_map[assigned_slot_id].vehicle_no = vehicle_no
            floor.slot_map[assigned_slot_id].vehicle_type = vehicle_type
            floor.slot_map[assigned_slot_id].expire_at = now + self.default_parking_time

        # Release lock & process payment
        with floor.lock:
            amt = ParkingRate.FOUR_WHEELER.value if vehicle_type == VehicleType.FOUR_WHEELER else ParkingRate.TWO_WHEELER.value
            payment_receipt = self.payment_strategy.pay(amt=amt)

        # handling payment failure
        if payment_receipt.status == PaymentStatus.FAIL:
            with floor.lock:
                floor.slot_map[assigned_slot_id].vehicle_no = 'empty'
                floor.slot_map[assigned_slot_id].expire_at = 0.0
                target_set.add(assigned_slot_id)
                raise ValueError("Payment failed. Slot not booked.")

        return floor.slot_map[assigned_slot_id], payment_receipt



    def book_slot(self, vehicle_no: str , vehicle_type: VehicleType, floor_no: int) -> Tuple[ParkingSlot, PaymentReceipt]:

        if floor_no not in self.parking_lot.floor_map:
            raise ValueError(f"Incorrect floor no: {floor_no} provided")

        now = time.time()
        with self._lock:

            # map of all slots in particular floor
            floor_slot_map = self.parking_lot.floor_map[floor_no]
            assigned_parking_slot = None
            # add check to see if all slots are full or not
            for id, parking_slot in floor_slot_map.slot_map.items():
                map = floor_slot_map.slot_map[id]
                # slot availability check
                if map.vehicle_no not in ['empty', vehicle_no] and map.vehicle_type == vehicle_type:
                    continue

                floor_slot_map.slot_map[id].vehicle_no = vehicle_no
                floor_slot_map.slot_map[id].vehicle_type = vehicle_type
                assigned_parking_slot = floor_slot_map.slot_map[id]
                assigned_parking_slot.expire_at = now + self.default_parking_time
                break

            if assigned_parking_slot is None:
                raise Exception(f"All {vehicle_type.name} slots on floor {floor_no} are full")

            amt = ParkingRate.FOUR_WHEELER.value if vehicle_type == VehicleType.FOUR_WHEELER else ParkingRate.TWO_WHEELER.value
            payment_receipt = self.payment_strategy.pay(amt=amt)

            if payment_receipt.status == PaymentStatus.FAIL:
                assigned_parking_slot.vehicle_no = 'empty'
                assigned_parking_slot.expire_at = 0.0
                raise ValueError("Payment failed. Slot not booked.")

            return assigned_parking_slot, payment_receipt


    def release_slot(self, parking_slot: ParkingSlot, floor_no: int) -> Union[PaymentReceipt, None]:
        floor = self.parking_lot.floor_map[floor_no]
        current_time = time.time()
        with floor.lock:
            if parking_slot.vehicle_no == 'empty':
                return None
            diff_secs = int(current_time - parking_slot.expire_at)
            if diff_secs < 0:
                return None

            print(f"extra secs cnt: {diff_secs}")

        with floor.lock:
            payment_receipt = None
            if diff_secs > 0:
                pending_amt = diff_secs * ParkingRate.FOUR_WHEELER.value if parking_slot.vehicle_type == VehicleType.FOUR_WHEELER else diff_secs * ParkingRate.TWO_WHEELER.value
                payment_receipt = self.payment_strategy.pay(amt=pending_amt)


        if payment_receipt.status == PaymentStatus.FAIL:
            return None

        floor.available_2w_ids.add(parking_slot.id) if parking_slot.vehicle_type == VehicleType.TWO_WHEELER else floor.available_4w_ids.add(parking_slot.id)
        parking_slot.vehicle_no = 'empty'
        parking_slot.expire_at = 0.0


        return payment_receipt


if __name__ == "__main__":
    # init
    num_slots = 100 # per floor
    default_parking_time = 2
    num_floors = 4

    parking_lot = ParkingLot()
    for floor_id in range(1, num_floors+1):
        parking_floor = ParkingFloor(id=floor_id)
        slots = []
        for slot_id in range(1, num_slots+1):
            if slot_id <= num_slots // 2:
                parking_slot = ParkingSlot(id=slot_id, vehicle_type=VehicleType.TWO_WHEELER, expire_at=0.0)
                slots.append(parking_slot)
            else:
                parking_slot = ParkingSlot(id=slot_id, vehicle_type=VehicleType.FOUR_WHEELER, expire_at=0.0)
                slots.append(parking_slot)

        for slot in slots:
            parking_floor.slot_map[slot.id] = slot
            parking_floor.available_2w_ids.add(slot.id) if slot.vehicle_type == VehicleType.TWO_WHEELER else parking_floor.available_4w_ids.add(slot.id)

        parking_lot.floor_map[floor_id] = parking_floor

    cc_pay = CreditCardPaymentStrategy(cc_no="abc123")
    upi_pay = UPIPaymentStrategy(vpa="abc@ptsbi")

    slot_booking_service = SlotBookingService(parking_lot=parking_lot, payment_strategy=cc_pay, default_parking_time=default_parking_time)

    assigned_parking_slot1, payment_receipt = slot_booking_service.book_slot_v2(vehicle_no="DL9CBB5204", vehicle_type=VehicleType.FOUR_WHEELER, floor_no=1)
    print(f'Payment Receipt generated - {payment_receipt}')
    print(f"Parking slot assigned - ", assigned_parking_slot1 )
    assigned_parking_slot2, payment_receipt = slot_booking_service.book_slot_v2(vehicle_no="DL9SAB4567", vehicle_type=VehicleType.TWO_WHEELER, floor_no=3)
    print(f'Payment Receipt generated - {payment_receipt}')
    print(f"Parking slot assigned - ", assigned_parking_slot2)

    print("Waiting for 3 secs")
    time.sleep(3)
    payment_receipt1 = slot_booking_service.release_slot(assigned_parking_slot2, 3)
    print(f'Payment Receipt generated - {payment_receipt1}', assigned_parking_slot2.id)
    time.sleep(1)
    payment_receipt2 = slot_booking_service.release_slot(assigned_parking_slot1, 1)
    print(f'\nPayment Receipt generated - {payment_receipt2}')

    try:
        # simulate failure
        cc_pay.simulate_failure = True
        slot_booking_service.book_slot_v2(vehicle_no="DL9CBB5205", vehicle_type=VehicleType.FOUR_WHEELER, floor_no=1)
    except ValueError as e:
        print(f"Exception is {e}")


