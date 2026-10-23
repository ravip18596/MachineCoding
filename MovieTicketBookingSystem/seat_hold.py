from dataclasses import dataclass, field
import time
from typing import Dict, Optional, Any, List
from threading import Lock, Thread

# Seats State Machine -> Available, Hold, Booked
@dataclass
class Seat:
    id: str
    locked_by: Optional[str] = None
    expires_at: float = 0.0
    is_booked: bool = False


    def available(self, now: float) -> bool:
        if self.is_booked:
            return False

        # Seat is available if not locked by any user or time is expired  
        return self.locked_by is None or now >= self.expires_at

    def hold(self, user_id: str, expires_at: float) -> None:
        
        self.locked_by = user_id
        self.expires_at = expires_at

    def booked(self) -> None:
        self.is_booked = True
        self.expires_at = float('inf')

@dataclass
class SeatLockManager:
    seat_ids: List[str]
    ttl_seconds: float = 300
    lock: Any = field(
        default_factory=Lock,
        # init is set to False to make sure Lock is not intialised before seat map is generated
        init=False,
        repr=False
    )
    # How many seats are there with seat manager for which we are maintaing a map
    seats: Dict[str, Seat] = field(init=False)

    def __post_init__(self):
        self.seats = {seat_id: Seat(id=seat_id) for seat_id in self.seat_ids}

    def hold_seats(self, user_id: str, requested_seats: List[str]) -> bool:
        # Atomic all or nothing hold for acquiring seats
        now  = time.time()
        # with keyword is my context manager which handles setup and cleanup automatically 
        # even if an error occurs
        # safer than calling lock.acquire() and lock.release()
        with self.lock:
            # first we are checking if all of the requested seats can be acquired or not
            for seat_id in requested_seats:
                seat = self.seats[seat_id]
                # not seat is checked to see if accidently non-valid seat is not passed
                if not seat or not seat.available(now):
                    return False

            # once validation of all requested seats are done,
            # we finally put a hold or apply lock on all requested seats
            for seat_id in requested_seats:
                seat = self.seats[seat_id]
                seat.hold(user_id=user_id, expires_at=now + self.ttl_seconds)
        
            return True

    
    def confirm_booking(self, user_id: str, requested_seats: List[str]) -> bool:
        now = time.time()
        with self.lock:
            # Here doing validation that requested seat is ready to be booked or not
            for seat_id in requested_seats:
                seat = self.seats[seat_id]
                if (not seat
                    or now >= seat.expires_at
                    or seat.locked_by != user_id
                    or seat.is_booked):
                    return False
                
            # finally booking is done
            for seat_id in requested_seats:
                seat = self.seats[seat_id]
                seat.booked()

            return True


if __name__  == "__main__":
    seat_lock_manager = SeatLockManager(seat_ids=['A1', 'B1', 'C1'], ttl_seconds=2)

    def book(user_id: str, seats: List[str]):
        if seat_lock_manager.hold_seats(user_id=user_id, requested_seats=seats):
            print(f'{user_id} has put on hold {seats}')
        else:
            print(f"{user_id} Contention failed for {seats}")

    t1 = Thread(target=book, args=("Ravi", ["A1", "B1"]))
    t2 = Thread(target=book, args=("Sandhya", ["A1"]))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    # Because Ravi will have lock on seats A1 and B1 and Sandhya will not
    # Sandhya will not have any tickets on hold threfore sleeping for those 2 sec
    # so that lock will be release on A1 by that time
    print("\nWaiting for TTL expiry")
    time.sleep(2.1)

    book("Sandhya", ["A1"])

