# Design
# Inventory management system
# Design Patterns being used
# 1. Factory, 2. Strategy 3. Facade
import threading
import uuid
import time
from dataclasses import  dataclass, field
from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Optional, List, Union

class PaymentStatus(Enum):
    SUCCESS = auto()
    FAIL = auto()
    REFUND_SUCCESS = auto()
    REFUND_FAIL = auto()

@dataclass
class PaymentReceipt:
    txn_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    status: PaymentStatus = PaymentStatus.SUCCESS
    amount: float = 0.0


class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> PaymentReceipt:
        pass

    @abstractmethod
    def refund(self, amount: float) -> PaymentReceipt:
        pass

# implements PaymentStrategy
class CreditCardPaymentStrategy(PaymentStrategy):
    cc_no: str
    simulate_failure: bool = False
    def pay(self, amount: float) -> PaymentReceipt:
        payment_receipt = PaymentReceipt(amount=amount)
        if self.simulate_failure:
            payment_receipt.status = PaymentStatus.FAIL
        return payment_receipt

    def refund(self, amount: float) -> PaymentReceipt:
        payment_receipt = PaymentReceipt(amount=amount, status=PaymentStatus.REFUND_SUCCESS)
        if self.simulate_failure:
            payment_receipt.status = PaymentStatus.REFUND_FAIL
        return payment_receipt


@dataclass
class Order:
    payment_receipt: PaymentReceipt
    items: List[Optional['Inventory']]
    order_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    user_id: str = ''


@dataclass
class Inventory:
    id: int
    price: float
    locked_by: Optional[str] = None
    expire_at: float = 0.0
    lock: threading.RLock = field(default_factory=threading.RLock)

    def available(self) -> bool:
        return self.locked_by is None and self.expire_at == 0.0

    def release_hold(self):
        self.locked_by = None
        self.expire_at = 0.0


class InventoryService:
    def __init__(self, inventory_items: List[Inventory], payment_strategy: PaymentStrategy):
        self.inventory_items = inventory_items
        self.payment_strategy = payment_strategy

    def checkout(self, items: List[Inventory], user_id: str, default_expire_sec: int) -> Union[Order, None]:
        amt = 0.0
        available_items = []
        for item in items:
            now = time.time()
            with item.lock:
                if not item.available():
                    print(f"[checkout] Inventory item {item.id} is not available")
                    continue

                item.locked_by = user_id
                item.expire_at = now + default_expire_sec

                amt += item.price
                available_items.append(item)
        if len(available_items) == 0:
            print("[checkout] no available items")
            return None
        payment_receipt = self.payment_strategy.pay(amount=amt)
        order = Order(user_id=user_id, payment_receipt=payment_receipt, items=available_items)
        if payment_receipt.status == PaymentStatus.FAIL:
            print(f"[checkout] Order unsuccessful with id = {order.order_id}. Initiating order cancellation")
            self.cancel_order(order)
            return None

        # release hold on each item
        for item in order.items:
            with item.lock:
                if item.available():
                    item.release_hold()
                    print("[checkout] Releasing hold on item")

        print(f"[checkout] Order successful with id = {order.order_id}")
        return order

    def cancel_order(self, order: Order) -> PaymentReceipt:

        refund_amt = order.payment_receipt.amount
        # release hold on each item
        for item in order.items:
            with item.lock:
                if item.available():
                    item.release_hold()
                    print(f"[cancel_order] Releasing hold on item with id: {item.id}")

        payment_receipt = self.payment_strategy.refund(amount=refund_amt)
        if payment_receipt.status == PaymentStatus.REFUND_FAIL:
            print(f"[cancel_order] Refund of amt: {payment_receipt.amount} is unsuccessful.")
        elif payment_receipt.status == PaymentStatus.REFUND_SUCCESS:
            print(f"[cancel_order] Refund of amt: {payment_receipt.amount} is successful.")
        return payment_receipt


if __name__ == '__main__':
    users = ['Ravi', 'Sandhya']
    invs = [
        Inventory(id=1, price=100),
        Inventory(id=2, price=100),
        Inventory(id=3, price=200)
    ]

    strategy = CreditCardPaymentStrategy()
    service = InventoryService(inventory_items=[inv for inv in invs], payment_strategy=strategy)

    order1 = service.checkout(items=[invs[0], invs[1]], user_id=users[0], default_expire_sec=2)
    if order1:
        print(f"Successful order creation: {order1}")
    order2 = service.checkout(items=[invs[2], invs[1]], user_id=users[1], default_expire_sec=2)
    if order2:
        print(f"Successful order creation: {order2}")

    # initiate failure
    refund_receipt = service.cancel_order(order2)
    print(f"Refund receipt: {refund_receipt}")
