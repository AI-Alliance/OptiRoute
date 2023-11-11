from logic import Task
from logic.models.Place import Place
from logic.Solution import Solution
from logic.algorithms.Algorithm import Algorithm


class GreedyAlgorithm(Algorithm):

    def solve(self, task: Task) -> Solution:
        print("Problem Solved!")

        solution = Solution(task_id=task.id)
        return solution
