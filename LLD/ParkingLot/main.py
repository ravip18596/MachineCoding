from enum import Enum
from datetime import datetime
from uuid import uuid4

class VehicleType(Enum):
    TwoWheeler = 1
    Small = 2
    Medium = 3
    Large = 4

class Address:
    def __init__(self, zip_code, street, city, country):
        self.zip_code = zip_code
        self.street = street
        self.city = city
        self.country = country

    
class Vehicle:
    def __init__(self, license_no, vehicle_type) -> None:
        self.license_no = license_no
        self.type = vehicle_type


class ParkingSpot:
    def __init__(self, number) -> None:
        self.number = number
        self.free = True
        self.vehicle =  None

    def is_free(self):
        return self.free
    
    def assign_vehicle(self, vehicle: Vehicle):
        self.vehicle = vehicle
        self.free = False

    def remove_vehicle(self):
        self.vehicle = None
        self.free = True

class Ticket:
    def __init__(self, vehicle: Vehicle, spot: ParkingSpot) -> None:
        self.ticket_no = uuid4()
        self.start_time = datetime.now()
        self.end_time = None
        self.vehicle = vehicle
        self.parking_spot = spot



class ParkingFloor:
    def __init__(self, num_spots, floor_no) -> None:
        floor_no = floor_no
        self.spots = [ParkingSpot(i) for i in range(num_spots)]


class ParkingLot:
    def __init__(self, num_floors) -> None:
        self.floor = [ParkingFloor(100, i) for i in range(num_floors)]


if __name__ == '__main__':
