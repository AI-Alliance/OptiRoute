from abc import ABC, abstractmethod

from logic import Task, Solution


class Algorithm(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def solve(self, task: Task) -> Solution:
        pass

    def start_in_depo(self, depot, vehicles, vehicles_id_to_places_dict):
        for vehicle in vehicles:
            vehicles_id_to_places_dict[vehicle.vehicle_id] = [depot]
    def finish_in_depo(self, depot, vehicles, vehicles_id_to_places_dict):
        for vehicle in vehicles:
            route: list = vehicles_id_to_places_dict[vehicle.vehicle_id]
            if len(route) <= 1:
                vehicles_id_to_places_dict[vehicle.vehicle_id] = []
            else:
                vehicles_id_to_places_dict[vehicle.vehicle_id].append(depot)
