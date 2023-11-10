from logic import Task, AlgorithmManager, GreedyAlgorithm
from logic.Solution import Solution


from services.Service import Service
from services.SolutionService import SolutionService


class TaskService(Service):

    def __init__(self, solution_service: SolutionService):
        self.solution_service = solution_service
        self.tasks: list[Task] = []
        self.algorithm_manager = AlgorithmManager(algorithm=GreedyAlgorithm())

    def add(self, task: Task) -> None:
        self.tasks.append(task)
        solution: Solution = self.algorithm_manager.solve_task(task)
        self.solution_service.add(solution)

    def get_by_id(self, task_id: str) -> Task:
        pass
        # return filter(lambda t: t.id == task_id, self.tasks)[0]

    def get_all(self) -> list[Task]:
        return self.tasks
