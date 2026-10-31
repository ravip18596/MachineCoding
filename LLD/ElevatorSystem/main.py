"""
Design Patterns Used:
1. Facade Pattern: ElevatorSystem acts as the single high-level unified entry point for external clients (request_ride, step), encapsulating internal car state management and dispatch routing.
2. Strategy Pattern: ElevatorSystem maintains an aggregation reference (o--) to the abstract interface Strategy, realized by ZoneDispatchStrategy, making dispatch algorithms swappable at runtime without altering core elevator mechanisms.
3. Composition: ElevatorSystem has a strong ownership lifecycle (*--) over multiple ElevatorCar instances.

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
from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Dict, List, Set
import heapq

class Direction(Enum):
    UP = auto()
    DOWN = auto()
    IDLE = auto()

class ElevatorCar:
    def __init__(self, car_no:int):
        self.car_no = car_no
        self.direction: Direction = Direction.IDLE
        self.current_floor: int = 1
        self.up_floors: List[int] = []
        self.down_floors: List[int] = []

    def add_stop(self, target_floor: int):
        if target_floor == self.current_floor:
            return

        if target_floor > self.current_floor:
            # means going up
            if target_floor not in self.up_floors:
                heapq.heappush(self.up_floors, target_floor)
                self.direction = Direction.UP
        elif target_floor < self.current_floor:
            # means going down
            if -target_floor not in self.down_floors:
                # We are just queuing requests which will be serviced later on
                heapq.heappush(self.down_floors, -target_floor)
                # No need to set this self.direction = Direction.DOWN because we do not want elevator car to stop
                # serving its current direction vector

        if self.direction == Direction.IDLE:
            if target_floor > self.current_floor:
                self.direction = Direction.UP
            else:
                self.direction = Direction.DOWN

    # this method implements LOOK algorithm
    def step(self):
        if self.direction == Direction.UP:
            if len(self.up_floors) > 0:
                self.current_floor = heapq.heappop(self.up_floors)
                if len(self.up_floors) == 0:
                    # meaning all my requests have been fulfilled in up direction then change direction
                    self.direction = Direction.DOWN if len(self.down_floors) > 0 else Direction.IDLE
            elif len(self.up_floors) == 0:
                # meaning all my requests have been fulfilled in up direction then change direction
                self.direction = Direction.DOWN if len(self.down_floors) > 0 else Direction.IDLE
                self.step()
        elif self.direction == Direction.DOWN:
            if len(self.down_floors) > 0:
                self.current_floor = -heapq.heappop(self.down_floors)
                if len(self.down_floors) == 0:
                    self.direction = Direction.UP if len(self.up_floors) > 0 else Direction.IDLE
            elif len(self.down_floors) == 0:
                # meaning all my requests in down direction is fulfilled, lets change direction
                self.direction = Direction.UP if len(self.up_floors) > 0 else Direction.IDLE
                self.step()

    @property
    def pending_stop_counts(self):
        return len(self.up_floors) + len(self.down_floors)

# =====================================================================
# Strategy Pattern: Zone-Based Dispatching
# =====================================================================

# strategy is to help to route which elevator car among cars is selected.
class Strategy(ABC):
    @abstractmethod
    def select_car(self, cars: List[ElevatorCar], source_floor: int, destination_floor: int) -> ElevatorCar:
        pass

class ZoneDispatchStrategy(Strategy):
    def __init__(self, zone_config: Dict[str, List[int]], floor_config: Dict[str, Set[int]]):
        self.zone_config = zone_config
        self.floor_config = floor_config

    def _resolve_zone(self, source_floor: int, destination_floor: int):
        if source_floor == destination_floor:
            raise ValueError("Source and destination floors cannot be identical")

        for zone_name, floors in self.floor_config.items():
            if source_floor in floors and destination_floor in floors:
                return zone_name

        raise ValueError(f"No direct elevator exists between {source_floor} and {destination_floor}")

    def select_car(self, cars: List[ElevatorCar], source_floor: int, destination_floor: int) -> ElevatorCar:
        target_zone = self._resolve_zone(source_floor, destination_floor)
        eligible_car_ids = set(self.zone_config[target_zone])

        candidate_cars = [car for car in cars if car.car_no in eligible_car_ids]

        # Pick car with minimum stop count, tie-break by distance to pickup floor
        return min(
            candidate_cars,
            key= lambda car: (car.pending_stop_counts, abs(car.current_floor-source_floor))
        )


# =====================================================================
# Facade Pattern: System Controller
# =====================================================================
class ElevatorSystem:
    def __init__(self, num_cars: int, strategy: Strategy):
        self.cars = [ElevatorCar(i+1) for i in range(num_cars)]
        self.strategy = strategy

    def request_ride(self, source_floor: int, destination_floor: int) -> int:
        """ elevator lobby """
        elevator_car_assigned = self.strategy.select_car(self.cars, source_floor, destination_floor)
        elevator_car_assigned.add_stop(source_floor)
        elevator_car_assigned.add_stop(destination_floor)
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

    assigned_car = elevator_system.request_ride(source_floor=1, destination_floor=9)
    print(f"{assigned_car} no elevator car assigned for floor_no = 4 to 9")

    assigned_car = elevator_system.request_ride(source_floor=1, destination_floor=15)
    print(f"{assigned_car} no elevator car assigned for floor_no = 1 to 15")

    assigned_car = elevator_system.request_ride(source_floor=18, destination_floor=12)
    print(f"{assigned_car} no elevator car assigned for floor_no = 18 to 12")

    assigned_car = elevator_system.request_ride(source_floor=11, destination_floor=16)
    print(f"{assigned_car} no elevator car assigned for floor_no = 11 to 16")

    assigned_car = elevator_system.request_ride(source_floor=2, destination_floor=8)
    print(f"{assigned_car} no elevator car assigned for floor_no = 2 to 8")
