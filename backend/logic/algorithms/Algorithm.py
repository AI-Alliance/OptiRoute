from abc import ABC, abstractmethod

from logic import Task, Solution


class Algorithm(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def solve(self, task: Task) -> Solution:
        pass
