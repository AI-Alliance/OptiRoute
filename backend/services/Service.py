from abc import ABC, abstractmethod
class Service(ABC):
    @abstractmethod
    def add(self, entity):
        pass
    @abstractmethod
    def get_by_id(self, entity_id):
        pass
    @abstractmethod
    def get_all(self):
        pass
