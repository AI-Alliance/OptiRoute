from logic import Task
from logic.Client import Client
from logic.Solution import Solution
from logic.algorithms.Algorithm import Algorithm


class GreedyAlgorithm(Algorithm):

    def solve(self, task: Task) -> Solution:
        print("Problem Solved!")
        for i in range(0, task.clients_number):
            client = Client(i)

        solution = Solution(task_id=task.id)
        return solution
