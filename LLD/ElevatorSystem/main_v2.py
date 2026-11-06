# Desgin
# Mutiple elevators
# Multi set elevators serving low-rise floors and high rise floors separately
# We will implement zone dispatch algo for selecting which elevator car to select. Strategy design pattern will be used
# We will implement LOOK elevator car scheduling algo
# LOOK will allow elevator to service all ride requests in up and down directions without having to do full round from lobby
# to top and top to lobby.
import heapq
import random
from enum import Enum, auto
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import List, Set, Dict, Union

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
                self.direction = Direction.UP
                heapq.heappush(self.up_floors, target_floor)

        elif target_floor < self.current_floor:
            if self.direction == Direction.DOWN and -target_floor not in self.down_floors:
                heapq.heappush(self.down_floors, -target_floor)
            elif self.direction == Direction.IDLE:
                self.direction = Direction.DOWN
                heapq.heappush(self.down_floors, target_floor)

    def step(self):
        if self.direction == Direction.UP:
            if len(self.up_floors) > 0:
                serviced_floor = heapq.heappop(self.up_floors)
                print(f"Floor:{serviced_floor} pickup by elevator car:{self.car_no} in UP Direction")
                if len(self.up_floors) == 0:
                    # no floors left, now change direction
                    self.direction = Direction.DOWN if len(self.down_floors) >0 else Direction.IDLE
            elif len(self.up_floors) == 0:
                # no floors left, now change direction
                self.direction = Direction.DOWN if len(self.down_floors) > 0 else Direction.IDLE
                self.step()
        elif self.direction == Direction.DOWN:
            if len(self.down_floors) > 0:
                serviced_floor = -heapq.heappop(self.down_floors)
                print(f"Floor:{serviced_floor} pickup by elevator car:{self.car_no} in DOWN Direction")
                if len(self.down_floors) == 0:
                    self.direction = Direction.UP if len(self.up_floors) > 0 else Direction.IDLE
            elif len(self.down_floors) == 0:
                # no floors to be serviced left, change direction
                self.direction = Direction.UP if len(self.up_floors) > 0 else Direction.IDLE

    @property
    def pending_stop_counts(self) -> int:
        return len(self.up_floors) + len(self.down_floors)


class DispatchStrategy(ABC):
    @abstractmethod
    def select_elevator_car(self, source, destination: int) -> int:pass


@dataclass
class ZoneDispatchStrategy(DispatchStrategy):
    zone_config: Dict[str, List[int]]
    floor_config: Dict[str, Set[int]]

    def select_elevator_car(self, source, destination: int) -> int:
        if source == destination:
            raise ValueError("Source can't be same as destination")

        assigned_zone = ''
        for zone, floors in self.floor_config.items():
            if source in floors and destination in floors:
                assigned_zone = zone
                break

        selected_elevator_cars = self.zone_config[assigned_zone]
        return random.randrange(min(selected_elevator_cars), max(selected_elevator_cars))



class ElevatorManager:
    def __init__(self, car_ids: List[int], strategy: DispatchStrategy):
        self.cars = [ElevatorCar(i) for i in car_ids]
        self.strategy = strategy

    def step(self):
        for car in self.cars:
            car.step()

    def request_ride(self, source, destination: int):
        print(f"[request_ride] assigned ride from {source} to {destination}")
        selected_car = self.cars[self.strategy.select_elevator_car(source, destination)]
        print(f"[request_ride] selected elevator car is {selected_car}")
        selected_car.add_stop(source)
        selected_car.add_stop(destination)
        print(f"[request_ride] Elevator Car state:{selected_car} after adding source and destination\n")


if __name__ == '__main__':
    zone_config = {
        'low-rise': [1,2],
        'high-rise': [3,4]
    }

    floor_config = {
        'low-rise': set([i for i in range(1, 11)]),
        'high-rise': {1}.union(set([i for i in range(11,21)]))
    }

    zone_dispatch_strategy = ZoneDispatchStrategy(zone_config, floor_config)
    elevator_manager = ElevatorManager(car_ids=[1,2,3,4], strategy=zone_dispatch_strategy)

    elevator_manager.request_ride(1, 9)
    elevator_manager.step()
    elevator_manager.request_ride(1, 15)
    elevator_manager.step()
    elevator_manager.request_ride(18, 11)
    elevator_manager.step()
    elevator_manager.request_ride(15, 17)
    elevator_manager.step()