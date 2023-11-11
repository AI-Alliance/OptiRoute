from logic.Solution import Solution
from services.Service import Service


class SolutionService(Service):
    def __init__(self):
        self.solutions: list[Solution] = []

    def add(self, solution: Solution):
        self.solutions.append(solution)

    def get_by_id(self, solution_id: str) -> Solution:
       pass
       #return filter(lambda s: s.id == solution_id, self.solutions)[0]

    def get_all(self) -> list[Solution]:
        return self.solutions

    def get_by_task_id(self, task_id):
        return next((solution for solution in self.solutions if solution.task.id == task_id), None)
