from logic.models.Model import Model


class Place(Model):
    def __init__(self, place_id: int, demand: int, place_index:int):
        self.place_id = place_id
        self.demand = demand
        self.place_index = place_index
        print(f"Place {self.place_id} with demand {self.demand} was created!")

    @staticmethod
    def create_from_dict(place_dict: dict):
        place_id = place_dict['place_id']
        place_index = place_dict['place_index']
        demand = place_dict['demand']
        return Place(place_id, place_index, demand)