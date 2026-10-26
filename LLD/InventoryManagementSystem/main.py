import threading
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class PaymentState(Enum):
    SUCCESS = auto()
    FAIL = auto()
    REFUND_SUCCESS = auto()
    REFUND_FAIL = auto()


@dataclass
class PaymentReceipt():
    id: str
    txn_id: str
    amt: float
    payment_status: PaymentState


# Strategy Design Pattern
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, txn_id: str, amt: float) -> PaymentReceipt:
        pass

    @abstractmethod
    def refund(self, txn_id: str, amt: float) -> PaymentReceipt:
        pass

@dataclass
class CreditCardPaymentStrategy(PaymentStrategy):
    cc_no: str

    def pay(self, txn_id: str, amt: float) -> PaymentReceipt:
        print(f"[Payment Gateway] successfully paid by user. amt: {amt}")
        return PaymentReceipt(
            id=uuid.uuid4().hex,
            txn_id=txn_id,
            amt=amt,
            payment_status=PaymentState.SUCCESS
        )

    def refund(self, txn_id: str, amt: float) -> PaymentReceipt:
        print(f"[Payment Gateway] successfully refund back to the user. amt: {amt}")
        return PaymentReceipt(
            id=uuid.uuid4().hex,
            txn_id=txn_id,
            amt=amt,
            payment_status=PaymentState.REFUND_SUCCESS
        )


@dataclass
class UPIPaymentStrategy(PaymentStrategy):
    vpa: str
    simulate_failure: bool = False

    def pay(self, txn_id: str, amt: float) -> PaymentReceipt:
        if self.simulate_failure:
            print(f"[Payment Gateway] payment failed. amt: {amt} having txn_id = {txn_id}")
            return PaymentReceipt(
                id=uuid.uuid4().hex,
                txn_id=txn_id,
                amt=amt,
                payment_status=PaymentState.FAIL
            )

        print(f"[Payment Gateway] successfully paid by user. amt: {amt}")
        return PaymentReceipt(
            id=uuid.uuid4().hex,
            txn_id=txn_id,
            amt=amt,
            payment_status=PaymentState.SUCCESS
        )

    def refund(self, txn_id: str, amt: float) -> PaymentReceipt:
        if self.simulate_failure:
            print(f"[Payment Gateway] payment failed. amt: {amt} having txn_id = {txn_id}")
            return PaymentReceipt(
                id=uuid.uuid4().hex,
                txn_id=txn_id,
                amt=amt,
                payment_status=PaymentState.FAIL
            )

        print(f"[Payment Gateway] successfully refunded amt: {amt} to the user having txn_id = {txn_id}")
        return PaymentReceipt(
            id=uuid.uuid4().hex,
            txn_id=txn_id,
            amt=amt,
            payment_status=PaymentState.REFUND_FAIL
        )

@dataclass
class Inventory:
    id: str
    expires_at: float = 0.0
    locked_by: Optional[str] = None
    is_booked: bool = False
    txn_id: str = ''

    # check if inventory is available
    def available(self, now) -> bool:
        self.is_booked = False
        return now>=self.expires_at

    # inventory is booked by user_id and put on hold
    def hold(self, user_id: str, expires_at: float):
        self.locked_by = user_id
        self.expires_at = expires_at

    # inventory booking is confirmed
    def book(self, txn_id):
        self.txn_id = txn_id
        self.expires_at = float('inf')
        self.locked_by = None

    # inventory is released back to being available
    def release(self):
        self.is_booked = False
        self.txn_id = ''
        self.expires_at = 0.0


@dataclass
class InventoryBookingManager:
    inventory_ids: List[str]
    lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    ttl_seconds: float = 300
    inventories: Dict[str, Inventory] = field(init=False)

    def __post_init__(self):
        self.inventories = {inventory_id: Inventory(id=inventory_id) for inventory_id in self.inventory_ids}

    def hold_inventory(self, user_id: str, requested_inventories: List[str]):
        now = time.time()
        with self.lock:
            for inventory_id in self.inventory_ids:
                inventory = self.inventories[inventory_id]
                # basic validations
                if not inventory or not inventory.available(now):
                    return False

            for inventory_id in self.inventory_ids:
                inventory = self.inventories[inventory_id]
                inventory.hold(user_id=user_id, expires_at=now+self.ttl_seconds)
            return True


    def book_inventory(self, user_id: str, requested_inventories: List[str], txn_id: str) -> bool:
        now = time.time()
        with self.lock:
            for inventory_id in requested_inventories:
                inventory = self.inventories[inventory_id]
                # basic validation
                if not inventory or inventory.locked_by != user_id or now>=inventory.expires_at or inventory.is_booked:
                    return False

            for inventory_id in requested_inventories:
                inventory = self.inventories[inventory_id]
                inventory.book(txn_id=txn_id)
            return True

    def release_hold_on_inventory(self, user_id: str, requested_inventories: List[str]):
        with self.lock:
            for inventory_id in requested_inventories:
                inventory = self.inventories[inventory_id]
                if inventory and inventory.locked_by == user_id and not inventory.is_booked:
                    inventory.release()

    def cancel_booking(self, inventory_ids: List[str]) -> bool:
        with self.lock:
            for inventory_id in inventory_ids:
                inventory = self.inventories[inventory_id]
                # check if inventory is booked or not
                if not inventory or not inventory.is_booked:
                    return False

            for inventory_id in inventory_ids:
                inventory = self.inventories[inventory_id]
                inventory.is_booked = False
                inventory.locked_by = None
                inventory.txn_id = ''
                inventory.expires_at = 0.0
            return True

@dataclass
class BookingOrder:
    order_id: str
    user_id: str
    txn_id: str
    amount: float
    inventory_ids: List[str]


@dataclass
class BookingService:
    inventory_booking_manager: InventoryBookingManager
    price_per_inventory: float

    def checkout(self, order_id: str, user_id: str, txn_id: str, inventory_ids: List[str], payment_strategy: PaymentStrategy) -> Optional[BookingOrder]:
        """ Orchestrate Lock -> Pay -> Confirm (or rollback on failure)"""
        print(f"[Checkout] Init checkout for {order_id} {user_id}")
        hold_status = self.inventory_booking_manager.hold_inventory(user_id, inventory_ids)
        if not hold_status:
            print(f"[Checkout] Inventory not available for inventory_ids: {inventory_ids}")
            return None
        print(f"[Checkout] Proceed to Payment")

        amount = self.price_per_inventory * len(inventory_ids)
        receipt = payment_strategy.pay(txn_id=txn_id, amt=amount)
        if receipt.payment_status.SUCCESS:
            confirmed = self.inventory_booking_manager.book_inventory(user_id, inventory_ids, txn_id=txn_id)
            if confirmed:
                order =  BookingOrder(
                    order_id=order_id,
                    user_id=user_id,
                    txn_id=txn_id,
                    amount=amount,
                    inventory_ids=inventory_ids
                )
                print(f"[Checkout] Payment for requested order: {order} is successful.")
                return order
            else:
                print(f"[Checkout] Payment is successful but inventory already booked. Init refund")
        else:
            print(f"[Checkout] Payment for requested order is unsuccessful.")
            self.inventory_booking_manager.release_hold_on_inventory(user_id=user_id, requested_inventories=inventory_ids)
            return None

    def cancel_booking(self, order: BookingOrder, txn_id: str, payment_strategy: PaymentStrategy):
        print("[cancel_booking] Init order cancellation")
        # Step 1: Refund the amount to the customer
        refund_pay_receipt = payment_strategy.refund(txn_id=txn_id, amt=order.amount)
        if refund_pay_receipt.payment_status == PaymentState.REFUND_SUCCESS:
            print(f"[cancel_booking] Refund of amount Rs. {order.amount} is successful")
        else:
            print(f"[cancel_booking] Refund of amount Rs. {order.amount} is unsuccessful")
        # Step 2: Release hold on inventory
        status = self.inventory_booking_manager.cancel_booking(order.inventory_ids)
        if status:
            print(f"[cancel_booking] Cancel inventory booking of Rs.{order.amount} is successful")
        else:
            print(f"[cancel_booking]  Cancel inventory booking of Rs.{order.amount} is unsuccessful")


if __name__ == '__main__':
    inv_booking_manager = InventoryBookingManager(inventory_ids=["I1", "I2", "I3"], ttl_seconds=2.0)
    inventory_service = BookingService(inv_booking_manager, 300)

    cc_payment_strategy = CreditCardPaymentStrategy(cc_no="abc123")
    upi_payment_strategy = UPIPaymentStrategy(vpa="abc@ybl")
    upi_payment_fail_strategy = UPIPaymentStrategy(vpa="abc@ybl", simulate_failure=True)

    order1 = inventory_service.checkout(
        order_id="o1",
        user_id="Ravi",
        txn_id='txn_12',
        inventory_ids=["I1", "I2"],
        payment_strategy=cc_payment_strategy
    )

    order2 = inventory_service.checkout(
        order_id="o2",
        user_id="Sandhya",
        txn_id='txn_23',
        inventory_ids=["I2", "I3"],
        payment_strategy=upi_payment_strategy
    )

    order3 = inventory_service.checkout(
        order_id="o3",
        user_id="Soni",
        txn_id='txn_13',
        inventory_ids=["I1","I3"],
        payment_strategy=upi_payment_fail_strategy
    )

    inventory_service.cancel_booking(
        order=order1,
        txn_id='txn_21',
        payment_strategy=cc_payment_strategy
    )
