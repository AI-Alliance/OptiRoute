import uuid


class Task:
    def __init__(self):
        self._id: str = ""
        self._distance_matrix = None
        self._places: list = []
        self._vehicles: list = []
        print("Task created!")

    @property
    def id(self):
        return self._id

    @property
    def distance_matrix(self):
        return self._distance_matrix

    @property
    def places(self):
        return self._places

    @property
    def vehicles(self):
        return self._vehicles

    def to_dict(self) -> dict:
        return {
            "id": self._id,
        }


class TaskBuilder:
    def __init__(self):
        self.task = Task()

    def set_id(self, id: str):
        self.task._id = id
        return self

    def set_distance_matrix(self, distance_matrix):
        self.task._distance_matrix = distance_matrix
        return self

    def set_places(self, places: list):
        self.task._places = places
        return self

    def set_vehicles(self, vehicles: list):
        self.task._vehicles = vehicles
        return self

    def get_task(self) -> Task:
        return self.task
