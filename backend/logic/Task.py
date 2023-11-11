import uuid


class Task:
    def __init__(self):
        self.id: str = str(uuid.uuid4())
        self.distance_matrix = None

        print("Task created!")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
        }


class TaskBuilder:
    def __init__(self):
        self.task = Task()

    def set_distance_matrix(self, distance_matrix):
        self.task.distance_matrix = distance_matrix
        return self

    def get_task(self) -> Task:
        return self.task
