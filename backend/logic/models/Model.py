from abc import ABC, abstractmethod


class Model(ABC):
    @staticmethod
    @abstractmethod
    def create_from_dict(model_dict: dict):
        pass
