import uuid


class Task:
    def __init__(self):
        # TODO implement task
        self.id: str = str(uuid.uuid4())

        self.clients_number: int = 0

        print("Task created!")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "clients_number": self.clients_number
        }


class TaskBuilder:
    def __init__(self):
        self.task = Task()

    def set_clients_number(self, clients_number: int):
        self.task.clients_number = clients_number
        return self

    def get_task(self) -> Task:
        return self.task
