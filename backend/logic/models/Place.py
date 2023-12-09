from logic.models.Model import Model


class Place(Model):
    def __init__(self, place_id: str, demand: int, place_index:int):
        self._place_id: str = place_id
        self._demand: int = demand
        self._place_index: int= place_index
        # print(f"Place {self._place_id} with demand {self._demand} was created!")
    @property
    def place_id(self):
        return self._place_id

    @property
    def demand(self):
        return self._demand

    @property
    def place_index(self):
        return self._place_index

    @staticmethod
    def create_from_dict(place_dict: dict):
        place_id = place_dict['place_id']
        demand = place_dict['demand']
        place_index = place_dict['place_index']

        return Place(place_id, demand, place_index)

    def to_dict(self):
        return {
                    "place_id": self._place_id,
                    "place_index": self._place_index,
                    "demand": self._demand
                }
