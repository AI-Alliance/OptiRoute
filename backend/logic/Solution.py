import uuid

from logic import Task
from logic.models import Place
from .utils import get_place_by_id, calculate_distance


class Solution:
    def __init__(self, task: Task, vehicles_to_places_dict: dict):
        self._id: str = str(uuid.uuid4())
        self._task: Task = task
        self._vehicle_route_dicts_list: list = self.create_vehicle_route_dictionaries_list(vehicles_to_places_dict)

        print("Solution created")

    @property
    def id(self):
        return self._id

    @property
    def task(self):
        return self._task

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "task_id": self.task.id,
            "vehicles": self._vehicle_route_dicts_list,
            "algorithm": self.task.algorithm_type.name
        }

    def create_vehicle_route_dictionaries_list(self, vehicles_to_places_dict: dict):
        dicts_list = []
        for vehicle_id, places_id_list in vehicles_to_places_dict.items():
            places = self.get_places_for_route(places_id_list)
            vehicle_route_dict = dict()
            vehicle_route_dict["vehicle_id"] = vehicle_id
            vehicle_route_dict["route"] = {
                "places": self.places_to_dict(places),
                "duration_sum": self.get_duration_sum(places)
            }
            dicts_list.append(vehicle_route_dict)

        return dicts_list
    def places_to_dict(self, places):
        return [place.to_dict()
                for place in places]

    def get_places_for_route(self, places_id_list: list[str]) -> list[Place]:
        return [get_place_by_id(self.task.places, place_id)
                for place_id in places_id_list]

    def get_duration_sum(self, places: list[Place]) -> int:
        duration_sum: int = 0
        for i in range(len(places)-1):
            place1 = places[i]
            place2 = places[i+1]
            duration_sum += calculate_distance(self.task.distance_matrix, place1, place2)
        return duration_sum

