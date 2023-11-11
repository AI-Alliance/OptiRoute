from logic.models.Model import Model


class Place(Model):
    def __init__(self, place_id: str, demand: int, place_index:int):
        self.place_id: str = place_id
        self.demand:int = demand
        self.place_index:int= place_index
        print(f"Place {self.place_id} with demand {self.demand} was created!")

    @staticmethod
    def create_from_dict(place_dict: dict):
        place_id = place_dict['place_id']
        demand = place_dict['demand']
        place_index = place_dict['place_index']

        return Place(place_id, demand, place_index)

    def to_dict(self):
        return {
                    "place_id": self.place_id,
                    "place_index": self.place_index,
                    "demand": self.demand
                },
