import uuid

from logic import Task
from logic.models import Place
from .utils import get_place_by_id

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
            "vehicles": self._vehicle_route_dicts_list
        }

    def create_vehicle_route_dictionaries_list(self, vehicles_to_places_dict: dict):
        dicts_list = []
        for vehicle_id, places_id_list in vehicles_to_places_dict.items():
            vehicle_route_dict = dict()
            vehicle_route_dict["vehicle_id"] = vehicle_id
            vehicle_route_dict["route"] = [get_place_by_id(self.task.places, place_id).to_dict()
                                             for place_id in places_id_list]
            dicts_list.append(vehicle_route_dict)
        return dicts_list


