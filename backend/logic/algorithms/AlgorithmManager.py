from logic import Task, Solution
from logic.algorithms.Algorithm import Algorithm


class AlgorithmManager:
    def __init__(self, algorithm: Algorithm):
        self.algorithm = algorithm

    def change_algorithm(self, algorithm: Algorithm):
        self.algorithm = algorithm

    def solve_task(self, task: Task) -> Solution:
        return self.algorithm.solve(task)
