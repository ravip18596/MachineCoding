Solution
--------

### UML

- User
  - user_id int
  - name    string
  - address location
  - phone_no string
  - email_id string

- Item
  - name string
  - price float
  - quantity int
  - weight   int

- OrderPriority
  - LOW
  - MEDIUM
  - HIGH

- OrderStatus
  - DELIVERED
  - IN_PROGRESS
  - DELIVERED


- Order
  - order_id    int
  - 

- Vehicle
  - id         int
  - vehicle_no string
  - capacity   int
  - curr_pos   Location
  - curr_status VehicleStatus

- VehicleStatus
  - AVAILBLE
  - OCCUPIED
  - NOT_WORKING


- Location
  - lat
  - lon

- PaymentMode
  - CREDIT_CARD
  - N

- PaymentStatus
  
- PaymentDetails

LogisticsSystem
  - orders []Order
  - vehicles []Vehicle
  - users []User
