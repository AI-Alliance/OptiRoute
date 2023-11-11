import uuid

from logic import Task
from logic.models import Place


class Solution:
    def __init__(self, task: Task, vehicles_to_places_dict: dict):
        self.id: str = str(uuid.uuid4())
        self.task: Task = task
        self.vehicle_route_dicts_list: list = self.get_vehicle_route_dictionaries_list(vehicles_to_places_dict)
        print("Solution created")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "task_id": self.task.id,
            "vehicles": self.vehicle_route_dicts_list
        }

    def get_vehicle_route_dictionaries_list(self, vehicles_to_places_dict: dict):
        dicts_list = []
        for vehicle_id, places_id_list in vehicles_to_places_dict.items():
            vehicle_route_dict = dict()
            vehicle_route_dict["vehicle_id"] = vehicle_id
            vehicle_route_dict["route"] = [self.get_place_by_id(place_id).to_dict() for place_id in places_id_list]
            dicts_list.append(vehicle_route_dict)
        return dicts_list

    def get_place_by_id(self, place_id: str) -> Place:
        return next((place for place in self.task.places if place.place_id == place_id), None)
