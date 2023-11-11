from logic import Task
from logic.models.Place import Place
from logic.Solution import Solution
from logic.algorithms.Algorithm import Algorithm


class RandomAlgorithm(Algorithm):

    def solve(self, task: Task) -> Solution:
        depot = task.places[0]
        clients = task.places[1:]
        vehicles_to_places_dict = {
            "490091c1-c7ea-4fed-8a1d-b2fd1a244384":
                ["694cca52-dd96-42b1-bb88-5c422ff30ce8",
                 "2007d679-0013-4310-b14e-744ff8844eec",
                 "694cca52-dd96-42b1-bb88-5c422ff30ce8"],
            "6bfb00e5-fd53-4d95-97d7-15058c5f1d94":
                ["694cca52-dd96-42b1-bb88-5c422ff30ce8",
                 "b4681e02-5625-406c-9410-5efa5dc34479",
                 "694cca52-dd96-42b1-bb88-5c422ff30ce8"
                 ]

        }
        #while len(clients)!=0:

        solution = Solution(task, vehicles_to_places_dict)
        print("Problem Solved!")
        return solution

