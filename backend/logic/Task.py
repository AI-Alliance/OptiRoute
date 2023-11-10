import uuid


class Task:
    def __init__(self):
        self.id: str = str(uuid.uuid4())
        self.vehicles_number: int = 0
        self.clients_number: int = 0
        self.distance_matrix = None

        print("Task created!")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "vehicles_number": self.vehicles_number,
            "clients_number": self.clients_number,

        }


class TaskBuilder:
    def __init__(self):
        self.task = Task()

    def set_clients_number(self, clients_number: int):
        self.task.clients_number = clients_number
        return self

    def set_vehicles_number(self, vehicles_number: int):
        self.task.vehicles_number = vehicles_number
        return self

    def set_distance_matrix(self, distance_matrix):
        self.task.distance_matrix = distance_matrix
        return self

    def get_task(self) -> Task:
        return self.task
