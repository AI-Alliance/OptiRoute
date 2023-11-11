from logic.models.Model import Model


class Vehicle(Model):
    def __init__(self, vehicle_id: int, capacity: int):
        self.vehicle_id = vehicle_id
        self.capacity = capacity
        print(f"Vehicle {self.vehicle_id}  with capacity {self.capacity}  was created!")

    @staticmethod
    def create_from_dict(place_dict: dict):
        vehicle_id = place_dict['vehicle_id']
        capacity = place_dict['capacity']
        return Vehicle(vehicle_id, capacity)
