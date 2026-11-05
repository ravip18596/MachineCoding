from enum import Enum, auto
from typing import List, Dict, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import heapq

# min_heap -> low rise
# max_heap -> high rise

class Direction(Enum):
    UP = auto()
    DOWN = auto()
    IDLE = auto()

@dataclass
class ElevatorCar:
    car_no: int
    current_floor: int = 1
    direction: Direction = Direction.IDLE
    up_floors: List[int] = field(default_factory=list)
    down_floors: List[int] = field(default_factory=list)

    def add_stop(self, target_floor: int):
        if target_floor > self.current_floor:
            if self.direction == Direction.UP and target_floor not in self.up_floors:
                heapq.heappush(self.up_floors, target_floor)
            elif self.direction == Direction.IDLE:
                heapq.heappush(self.up_floors, target_floor)
                self.direction = Direction.UP

        elif target_floor < self.current_floor:
            if self.direction == Direction.DOWN and -target_floor not in self.down_floors:
                heapq.heappush(self.down_floors, -target_floor)
            elif self.direction == Direction.IDLE:
                heapq.heappush(self.down_floors, -target_floor)
                self.direction = Direction.DOWN

    # implements LOOK algorithm
    def step(self):
        if self.direction == Direction.UP:
            if len(self.up_floors) > 0:
                self.current_floor = heapq.heappop(self.up_floors)
                if len(self.up_floors) == 0:
                    self.direction = Direction.DOWN if len(self.down_floors) > 0 else Direction.IDLE
            elif len(self.up_floors) == 0:
                self.direction = Direction.DOWN if len(self.down_floors) > 0 else Direction.IDLE
                self.step()
        elif self.direction == Direction.DOWN:
            if len(self.down_floors) > 0:
                self.current_floor = -heapq.heappop(self.down_floors)
                if len(self.down_floors) == 0:
                    self.direction = Direction.UP if len(self.up_floors) > 0 else Direction.IDLE
            elif len(self.down_floors) == 0:
                self.direction = Direction.UP if len(self.up_floors) > 0 else Direction.IDLE
                self.step()

    @property
    def pending_stops(self):
        return len(self.up_floors) + len(self.down_floors)

class DispatchStrategy(ABC):
    @abstractmethod
    def select_elevator_car(self, cars: List[ElevatorCar], source: int, destination: int) -> ElevatorCar:
        pass


@dataclass
class ZoneDispatchStrategy(DispatchStrategy):
    zone_config: Dict[str, List[int]]
    floor_config: Dict[str, Set[int]]

    def select_elevator_car(self, cars: List[ElevatorCar], source: int, destination: int) -> ElevatorCar:
        # resolving zone
        if source == destination:
            raise ValueError("Source and destination cannot be the same")
        """
        floor_config = {
            'low-rise': set([i for i in range(1, 11)]),
            'high-rise': {1}.union(set(i for i in range(11, 21)))
        }
        """
        assigned_zone = ''
        zone_cars = []
        for zone, floors in self.floor_config.items():
            if source in floors and destination in floors:
                assigned_zone = zone
                zone_cars = self.zone_config[assigned_zone]
                break

        if not assigned_zone:
            raise ValueError("No elevator car available to service request")

        candidate_cars = [car for car in cars if car.car_no in zone_cars]
        return min(candidate_cars, key=lambda car: (car.pending_stops, abs(source - car.current_floor)))

# Facade Design Pattern
class ElevatorManager:
    def __init__(self, elevator_cars: List[int], strategy: DispatchStrategy):
        self.elevator_cars = [ElevatorCar(car_no=car_id) for car_id in elevator_cars]
        self.strategy = strategy

    def request_ride(self, source: int, destination: int):
        print(f"[Elevator Manager] requested ride from source:{source} to destination:{destination}")
        assigned_car = self.strategy.select_elevator_car(cars=self.elevator_cars, source=source, destination=destination)
        assigned_car.add_stop(source)
        assigned_car.add_stop(destination)
        print(f"[Elevator Manager]: assigned elevator car is {assigned_car}")
        print(f"[Elevator Manager]: added source:{source}, destination:{destination} to assigned car\n")
        self.step()

    def step(self):
        for car in self.elevator_cars:
            car.step()


if __name__ == '__main__':
    # suppose there are 4 elevator cars
    zone_config = {
        'low-rise': [1, 2],
        'high-rise': [3, 4]
    }

    floor_config = {
        'low-rise': set([i for i in range(1,11)]),
        'high-rise': {1}.union(set(i for i in range(11, 21)))
    }

    zone_dispatch = ZoneDispatchStrategy(zone_config=zone_config, floor_config=floor_config)
    elevator_manager = ElevatorManager(elevator_cars=[1,2,3,4], strategy=zone_dispatch)

    elevator_manager.request_ride(source=1, destination=9)
    elevator_manager.step()

    elevator_manager.request_ride(source=4, destination=8)
    elevator_manager.step()

    elevator_manager.request_ride(source=1, destination=15)
    elevator_manager.step()

    elevator_manager.request_ride(source=13, destination=1)
    elevator_manager.step()

    elevator_manager.request_ride(source=18, destination=1)
    elevator_manager.step()
