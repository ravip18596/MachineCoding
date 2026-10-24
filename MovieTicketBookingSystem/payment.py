# #####################
# Design Pattern Used #
# #####################

# 1. Strategy Design Pattern: Decouples payment method (CreditCar, UPI, NetBanking)
# 2. Saga or 2-phase-commit design
# 2.1. Phase 1: Hold: Requested Inventory is locked with a TTL
# 2.2. Phase 2: Charge: Invoke payment strategy
# 2.3. Phase 3: Commit or Compensate: Once payment is confirmed, then we call `confirm_booking`
#      else call `release_hold()` to revoke lock on requested inventory

import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum, auto
from abc import ABC, abstractmethod
from uuid import uuid4
from collections import defaultdict
from threading import Lock

class PaymentState(Enum):
    FAIL = auto()
    SUCCESS = auto()
    REFUND_SUCCESS = auto()
    REFUND_FAILED = auto()

@dataclass(frozen=True)
class PaymentReceipt:
    transaction_id: str
    payment_status: PaymentState

class PaymentStrategy(ABC):
    "payment mode interface"
    @abstractmethod
    def pay(self, transaction_id: str, amount: float) -> PaymentReceipt:
        pass

    @abstractmethod
    def refund(self, transaction_id: str, amount: float) -> PaymentReceipt: 
        pass

class CreditCardPayment(PaymentStrategy):
    def __init__(self, card_number: str):
        self.card_number = card_number

    def pay(self, transaction_id: str, amount: float) -> PaymentReceipt:
        print(f"[Payment Gateway] Payment of Rs {amount:.2f} to card number: {self.card_number} is successful")
        return PaymentReceipt(
            transaction_id=transaction_id,
            payment_status=PaymentState.SUCCESS
        )

    def refund(self, transaction_id: str, amount: float) -> PaymentReceipt:
        print(f"[Payment Gateway] Refund of Rs {amount:.2f} to card number: {self.card_number} having txn_id: {transaction_id}")
        return PaymentReceipt(
            transaction_id=transaction_id,
            payment_status=PaymentState.REFUND_SUCCESS
        )

class UPIPayment(PaymentStrategy):
    def __init__(self, vpa: str, simulate_failure: bool = False):
        self.vpa = vpa
        self.simulate_failure = simulate_failure

    def pay(self, amount: float, transaction_id: str) -> PaymentReceipt:
        print(f"[Payment Gateway] Payment of Rs. {amount:.2f} to UPI address {self.vpa} is unsuccessful ")
        if self.simulate_failure:
            return PaymentReceipt(
                transaction_id=transaction_id,
                payment_status=PaymentState.FAIL
            )
        print(f"[Payment Gateway] Payment of Rs. {amount:.2f} to UPI address {self.vpa} is successful ")
        return PaymentReceipt(
            transaction_id=transaction_id,
            payment_status=PaymentState.SUCCESS,
        )

    def refund(self, transaction_id: str, amount: float) -> PaymentReceipt:
        if self.simulate_failure:
            print(f"[Payment Gateway] Refund of Rs. {amount:.2f} failed ")
            return PaymentReceipt(
                transaction_id=transaction_id,
                payment_status=PaymentState.REFUND_FAILED
            )
        print(f"[Payment Gateway] Refund of Rs. {amount:.2f} succeded.")
        return PaymentReceipt(
            transaction_id=transaction_id,
            payment_status=PaymentState.REFUND_SUCCESS
        )
        

        

# no frozen dataclass because seat's fields can change
# States - available -> hold -> book then release
@dataclass
class Seat:
    id: str
    locked_by: Optional[str] = None
    is_booked: bool = False
    expire_at: float = 0.0
    transaction_id: str = ''
    

    def available(self, now) -> bool:
        if self.is_booked:
            return False
        return self.locked_by is None or now>=self.expire_at

    def hold(self, user_id: str, expire_at: float) -> None:
        self.locked_by = user_id
        self.expire_at = expire_at


    def release(self) -> None:
         self.locked_by = None
         self.expire_at = 0.0

    def book(self, transaction_id: str) -> None:
        self.is_booked = True
        self.expire_at = float('inf')
        self.transaction_id = transaction_id
        

@dataclass
class SeatBookingManager:
    seat_ids: List[str]
    ttl_seconds: float
    lock: Lock = field(
        default_factory=Lock,
        init=False,
        repr=False
    )
    # seat id to Seat Map
    seats: Dict[str, Seat] = field(init=False)

    def __post_init__(self):
        self.seats = {seat_id: Seat(id=seat_id) for seat_id in self.seat_ids}

    def hold_seats(self, user_id: str, requested_seats: List[str]) -> bool:
        # automatic all or nothing hold for acquiring seats
        now = time.time()
        with self.lock:
            for seat_id in requested_seats:
                seat = self.seats[seat_id]
                if not seat or not seat.available(now):
                    return False

            for seat_id in requested_seats:
                seat = self.seats[seat_id]
                seat.hold(user_id=user_id, expire_at=now+self.ttl_seconds)
            
            return True

    def confirm_booking(self, user_id: str, requested_seats: List[str], transaction_id: str) -> bool:
        now = time.time()
        with self.lock:
            for seat_id in requested_seats:
                seat = self.seats[seat_id]
                if (
                    not seat or
                    now >= seat.expire_at or
                    seat.locked_by != user_id or
                    seat.is_booked
                ):
                    return False
                

            for seat_id in requested_seats:
                seat = self.seats[seat_id]
                seat.book(transaction_id=transaction_id)

            return True

    def release_hold(self, user_id: str, requested_seats: List[str]) -> None:
        """ 
        This method is there to release hold explicitly without waiting for TTL expiry
        This will be called in saga pattern phase 3 -> revoking hold on inventory(seat) once payment is confirmed.
        """
        with self.lock:
            for seat_id in requested_seats:
                seat = self.seats[seat_id]
                if seat and seat.locked_by == user_id and not seat.is_booked:
                    seat.release()

    def cancel_booked_seats(self, seat_ids: List[str]) -> bool:
        # validate if seats are booked or not
        with self.lock:
            for seat_id in seat_ids:
                seat = self.seats[seat_id]
                if not seat or not seat.is_booked:
                    return False

            for seat_id in seat_ids:
                seat = self.seats[seat_id]
                seat.locked_by = None
                seat.is_booked = False
                seat.expire_at = 0.0

            return True


# ==========================================
# 3. Booking / Checkout Orchestrator Service
# ==========================================

@dataclass(frozen=True)
class BookingOrder:
    order_id: str
    user_id: str
    seat_ids: List[str]
    amount: float
    transaction_id: str


class BookingService:
    def __init__(
            self, seat_booking_manager: SeatBookingManager,
            price_per_seat: float = 150.0
        ) -> None:
        self.seat_booking_manager = seat_booking_manager
        self.price_per_seat = price_per_seat

    # Inventrory Lock -> Payment -> Confirm
    def checkout(
        self,
        order_id: str,
        user_id: str,
        seat_ids: List[str],
        transaction_id: str,
        paymentStrategy: PaymentStrategy
    ) -> Optional[BookingOrder]:
        """ 
        Orchestrates: Lock -> Pay -> Confirm (or Rollback on failure)
        """
        print(f"Init checkout for Order {order_id} ({user_id})")
        seat_hold_status = self.seat_booking_manager.hold_seats(
            user_id=user_id,
            requested_seats=seat_ids,
        )
        # 1. Attempt Hold status
        if not seat_hold_status:
            print(f"[Checkout] Not able to hold requested seats {seat_ids}.")
            return None
        print(f"[Checkout] Able to hold requested seats {seat_ids}. Proceeding to payment...")

        amount = self.price_per_seat * len(seat_ids)
        # 2. Charge through strategy pattern
        receipt = paymentStrategy.pay(transaction_id=transaction_id, amount=amount)
        if receipt.payment_status == PaymentState.SUCCESS:
            # 3. On successful payment, book inventory(seat)
            confirmed = self.seat_booking_manager.confirm_booking(user_id=user_id, requested_seats=seat_ids, transaction_id=transaction_id)
            if confirmed:
                order = BookingOrder(
                    order_id=order_id,
                    user_id=user_id,
                    seat_ids=seat_ids,
                    amount=amount,
                    transaction_id=transaction_id
                )
                print(f"[Checkout] Payment succeeded with status {PaymentState.SUCCESS} for amount {amount:.2f} with order_id: {order_id}")
                return order
            else:
                print(f"[Checkout] Payment is successful but seats {seat_ids} not booked. Auto refund can be triggered to customer")
                return None
        else:
            print(f"[Checkout] Payment failed with status {PaymentState.FAIL}")
            self.seat_booking_manager.release_hold(user_id=user_id, requested_seats=seat_ids)
            return None
        
    def cancel_booking(self, order: BookingOrder, payment_strategy: PaymentStrategy, transaction_id: str) -> None:
        print("Init order cancellation")
        # Step 1: Refund the amount to the customer
        refund_payment_receipt = payment_strategy.refund(
            transaction_id=transaction_id,
            amount=order.amount
        )
        if refund_payment_receipt.payment_status == PaymentState.REFUND_SUCCESS:
            print(f"[Refund] Refund of amount {order.amount} is successful")
        else:
            print(f"[Refund] Refund of amount {order.amount} is unsuccessful")
        
        # Step 2: Unbook the seats meaning release hold of inventory
        cancel_seats_status = self.seat_booking_manager.cancel_booked_seats(order.seat_ids)
        if cancel_seats_status:
            print(f"[Refund] Successfully cancelled booking for these seats {order.seat_ids}")
        else:
            print(f"[Refund] UnSuccessful in cancelling booking for these seats {order.seat_ids}")
        

        
if __name__ == "__main__":
    seat_booking_manager = SeatBookingManager(seat_ids=["A1","A2","B1", "B2"], ttl_seconds=2.0)
    booking_service = BookingService(
        seat_booking_manager=seat_booking_manager,
        price_per_seat=300.0    
    )
    cc_payment_strategy = CreditCardPayment(card_number="ABC")
    upi_payment_strategy = UPIPayment(vpa="abc@ybl")
    upi_fail_payment_strategy = UPIPayment(vpa="xyz@ptsbi", simulate_failure=True)

    order1 = booking_service.checkout(
        order_id="o1",
        user_id="Ravi",
        seat_ids=["A1", "A2"],
        paymentStrategy=cc_payment_strategy,
        transaction_id="A12"
    )
    print(f"[main] successful order booking. {order1}")
    order2 = booking_service.checkout(
        order_id="o2",
        user_id="Sandhya",
        seat_ids=["B1", "B2"],
        paymentStrategy=upi_payment_strategy,
        transaction_id="B12"
    )
    print(f"[main] successful order booking. {order2}")
    order3 = booking_service.checkout(
        order_id="o3",
        user_id="Ravi",
        seat_ids=["B1"],
        paymentStrategy=upi_fail_payment_strategy,
        transaction_id="B13"
    )
    print(f"[main] unsuccessful order booking. {order3}")

    booking_service.cancel_booking(order=order2, payment_strategy=cc_payment_strategy, transaction_id="B12")
