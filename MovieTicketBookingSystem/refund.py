from abc import ABC,abstractmethod
from typing import List
from payment import PaymentReceipt, BookingOrder

# This flow is when booing is confirmed but customer wants cancellation

# 1. Update Payment Strategy Interface

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> PaymentReceipt:
        pass

    @abstractmethod
    def refund(self, transaction_id: str, amount: float) -> bool:
        pass


# 2. Add Seat unbooking to SeatLockManager
def cancel_booked_seats(self, booked_seat_ids: List[str]) -> bool:
    with self.lock:
        # verify all seats are booked
        for seat_id in booked_seat_ids:
            seat = self.seats[seat_id]
            # seat is not None or seat is not booked.
            # return False because we cannot refund on unallocated seats
            if not seat or not seat.is_booked:
                return False

        # Reset to AVAILABLE
        for seat_id in booked_seat_ids:
            seat = self.seats[seat_id]
            seat.is_booked = False
            seat.locked_by = None
            seat.expire_at = 0.0
        return True

# 3. Add cancel_booking() in BookingManager

def cancel_booking(self, order: BookingOrder, payment_strategy: PaymentStrategy) -> bool:
    print(f"\n--- [cancel_booking] Init order cancellation for id: {order.order_id} ----")

    # Step A: Refund money via payment gateway
    refund_status = payment_strategy.refund(transaction_id=order.transaction_id, amount=order.amount)
    if not refund_status:
        print("[cancel_booking] Problem at the payment gateway. refund unsuccessful")
        return False
    # Step B: Free the movie ticket inventory
    booking_cancellation_status = self.seat_booking_manager.cancel_booked_seats(order.seat_ids)
    print(f"Status of booking cancellation for order: {order} having status {booking_cancellation_status}")
    return True