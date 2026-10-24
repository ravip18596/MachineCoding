# Functional Requirements

## User journey that we will be supporting

1. search movie by city
2. How to handle concurrent users booking same seat
   a. Seat hold using TTL
3. checkout and payment integration
4. booking cancellation and refund


# Non Functional Requirements

1. Special requirements to handle scale
2. Concurrency and seat locking mechanism


# Implementation

1. [Search movie by city](searchV2.py)
2. [Handle Concurrent Users booking same seat](seat_hold.py)
3. [checkout and payment](payment.py)
4. [booking cancellation and refund](refund.py)

