from abc import ABC, abstractmethod


class Model(ABC):
    @staticmethod
    @abstractmethod
    def create_from_dict(place_dict: dict):
        pass
