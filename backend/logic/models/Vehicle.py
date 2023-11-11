from logic.models.Model import Model


class Vehicle(Model):
    def __init__(self, vehicle_id: int, capacity: int):
        self._vehicle_id = vehicle_id
        self._capacity = capacity
        print(f"Vehicle {self._vehicle_id}  with capacity {self._capacity}  was created!")
    @property
    def vehicle_id(self):
        return self._vehicle_id
    @property
    def capacity(self):
        return self._capacity

    @staticmethod
    def create_from_dict(place_dict: dict):
        vehicle_id = place_dict['vehicle_id']
        capacity = place_dict['capacity']
        return Vehicle(vehicle_id, capacity)
