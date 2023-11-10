from logic import Task
from logic.Solution import Solution
from logic.algorithms.Algorithm import Algorithm


class GreedyAlgorithm(Algorithm):

    def solve(self, task: Task) -> Solution:
        print("Problem Solved!")
        result = Solution(task_id=task.id)
        return result
