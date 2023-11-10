from logic import Task
from services.Service import Service


class TaskService(Service):
    def __init__(self):
        self.tasks: list[Task] = []

    def add(self, task: Task) -> None:
        self.tasks.append(task)

    def get_by_id(self, task_id: str) -> Task:
        return filter(lambda t: t.id == task_id, self.tasks)[0]

    def get_all(self) -> list[Task]:
        return self.tasks
