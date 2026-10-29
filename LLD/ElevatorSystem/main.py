"""
Design Patterns Used:
1. Strategy Design Pattern
2. Facade Design Pattern

How the Components Interact Visually
    Zone Partitioning:
        Cars 1 & 2 are restricted to the Low-Rise band (Floors 1–10).

        Cars 3 & 4 are express/local to the High-Rise band (Floors 1, 11–20), skipping floors 2–10 during normal transit.
    Dispatch Filter:
        When a request is triggered (e.g., Floor 16, DOWN), the dispatcher immediately discards Cars 1 and 2 from consideration.

        Between Cars 3 and 4, it selects the car with fewer pending stops, breaking ties with physical distance.
    LOOK Execution:
        Within each car, the min/max heaps ensure that all requests along the car's current direction vector are cleared sequentially before reversing.

Trade-offs to Highlight in an Interview
    Pros: Eliminates the "stopping on every single floor" issue in high buildings; prevents cars from traversing the entire shaft height needlessly; minimizes round-trip transit times.
    Cons: Reduced redundancy—if Car 1 and Car 2 are undergoing maintenance, the Low-Rise zone loses service
"""
from enum import Enum
from abc import ABC, abstractmethod
from typing import Dict, List, Set
import heapq

class Direction(Enum):
    UP = 1
    DOWN = -1
    IDLE = 0

class ElevatorCar:
    def __init__(self, car_no:int):
        self.car_no = car_no
        self.direction: Direction = Direction.IDLE
        self.current_floor: int = 1
        self.up_floors: List[int] = []
        self.down_floors: List[int] = []

    def add_stop(self, floor_no: int, direction: Direction):pass

    def step(self):
        if self.direction == Direction.UP:
            if len(self.up_floors) > 0:
                self.current_floor = heapq.heappop(self.up_floors)
                if len(self.up_floors) == 0:
                    self.direction = Direction.DOWN if len(self.down_floors) > 0 else Direction.IDLE
            elif len(self.up_floors) == 0:
                self.direction = Direction.DOWN

        elif self.direction == Direction.DOWN:
            if len(self.down_floors) > 0:
                self.current_floor = -heapq.heappop(self.down_floors)
                if len(self.down_floors) == 0:
                    self.direction = Direction.UP if len(self.up_floors) > 0 else Direction.IDLE
            elif len(self.down_floors) == 0:
                # if no requests pending in up direction then simply change direction
                self.direction = Direction.UP

# =====================================================================
# Strategy Pattern: Zone-Based Dispatching
# =====================================================================

# strategy is to help to route which elevator car among cars is selected.
class Strategy(ABC):
    @abstractmethod
    def select_cars(self, cars: List[ElevatorCar], pickup_floor: int, direction: Direction) -> ElevatorCar:
        pass

class ZoneDispatchStrategy(Strategy):
    def __init__(self, zone_config: Dict[str, List[int]], floor_config: Dict[str, Set[int]]):
        self.zone_config = zone_config
        self.floor_config = floor_config

    def select_cars(self, cars: List[ElevatorCar], pickup_floor: int, direction: Direction) -> ElevatorCar:
        pass

# =====================================================================
# Facade Pattern: System Controller
# =====================================================================
class ElevatorSystem:
    def __init__(self, num_cars: int, strategy: Strategy):
        self.cars = [ElevatorCar(i+1) for i in range(num_cars)]
        self.strategy = strategy

    def request_pickup(self, floor_no: int, direction: Direction) -> int:
        """ elevator lobby """
        elevator_car_assigned = self.strategy.select_cars(self.cars, floor_no, direction)
        elevator_car_assigned.add_stop(floor_no, direction)
        return elevator_car_assigned.car_no

    def step(self) -> None:
        """ ticker to move all elevator cars one step"""
        for car in self.cars:
            car.step()


if __name__ == '__main__':
    zones_config = {
        "low_rise": [1, 2],
        "high_rise": [3, 4]
    }

    floor_config = {
        "low_rise": set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
        "high_rise": set([1, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
    }

    strategy = ZoneDispatchStrategy(zones_config, floor_config)
    elevator_system = ElevatorSystem(num_cars=4, strategy=strategy)

    assigned_car = elevator_system.request_pickup(floor_no = 15, direction=Direction.DOWN)
    print(f"{assigned_car} no elevator car assigned for floor_no = 15 DOWN")

    assigned_car = elevator_system.request_pickup(floor_no = 4, direction=Direction.UP)
    print(f"{assigned_car} no elevator car assigned for floor_no = 4 UP")
