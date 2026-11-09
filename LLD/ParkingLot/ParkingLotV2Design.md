# Parking Lot Design

```python

# 1. Enums
class VehicleType(Enum): TWO_WHEELER, FOUR_WHEELER
class PaymentStatus(Enum): SUCCESS, FAIL
class ParkingRate(Enum): TWO_WHEELER = 30, FOUR_WHEELER = 50

# 2. Core Models (State & Concurrency)
class ParkingSlot:
    # state: id, expire_at, vehicle_no, vehicle_type

class ParkingFloor:
    # state: id, slot_map (dict), available_2w_ids (set), available_4w_ids (set)
    # concurrency: lock (threading.RLock) - granular floor-level lock

class ParkingLot:
    # state: floor_map (dict)

# 3. Strategy Pattern (Extensible Payments)
class PaymentStrategy(ABC):
    def pay(self, amt: float) -> PaymentReceipt: pass

class CreditCardPaymentStrategy(PaymentStrategy): pass
class UPIPaymentStrategy(PaymentStrategy): pass

# 4. Facade Pattern (Service Layer)
class SlotBookingService:
    # state: parking_lot, payment_strategy, default_parking_time, floor_queue (capacity tracker)
    
    def book_slot(self, vehicle_no: str, vehicle_type: VehicleType) -> Tuple[ParkingSlot, PaymentReceipt]: pass
    def release_slot(self, parking_slot: ParkingSlot, floor_no: int) -> Union[PaymentReceipt, None]: pass
```

## Method wise Algo

### book_slot (vehicle_no, vehicle_type)

- fetch available floor from queue 
- Critical section 1
    - acquire lock
    - find target set from available 2w or 4w set
    - pop an available slot from target_set
    - update the parking_slot object (vehicle_no, vehicle_type, expire_at)
    - release_lock
- Process Payment (I/O bound)
  - calculate amt
  - pay amt using payment_starategy.pay()
  - This is done outside the thread to allow booking of other vehicles simultaneous
- Critical Section 2
  - Handle payment failure
  - Reset parking_slot object (vehicle_no, expire_at)
  - Add parking_slot_id back to the target_set

- Return Parking Slot and payment receipt.

### release_slot (parking_slot, floor_no)

- fetch floor using floor_no
- acquire floor lock
  - check diff_secs = current_time - expire_at
- Process Overdue Payment (I/O bound)
  - acquire floor lock
  - calculate overdue payment
  - payment_strategy.pay
  - do failure validations
- acquire floor lock
    - release slot back to 2w and 4w set
    - reset parking_slot obj
- Return PaymentReceipt

