from logic import Task
from logic.Solution import Solution
from logic.algorithms.Algorithm import Algorithm
from logic.models import Place
from logic.models.Vehicle import Vehicle


class GreedyAlgorithm(Algorithm):
    def solve(self, task: Task) -> Solution:
        depot: Place = task.places[0]
        clients = task.places[1:]
        vehicles: list[Vehicle] = task.vehicles
        unvisited_clients: list[Place] = clients.copy()

        vehicles_id_to_current_capacity = {}
        for vehicle in vehicles:
            vehicles_id_to_current_capacity[vehicle.vehicle_id] = vehicle.capacity

        vehicles_id_to_places_dict = {}

        # starting from depot
        for vehicle in vehicles:
            vehicles_id_to_places_dict[vehicle.vehicle_id] = [depot]

        while len(unvisited_clients) != 0:
            shortest_distance = float('inf')
            best_pair = (None, None)
            for vehicle in vehicles:
                last_place_visited_by_vehicle = vehicles_id_to_places_dict[vehicle.vehicle_id][-1]
                for client in unvisited_clients:
                    possible_distance = task.distance_matrix[last_place_visited_by_vehicle.place_index][
                        client.place_index]
                    if vehicles_id_to_current_capacity[
                        vehicle.vehicle_id] >= client.demand and possible_distance < shortest_distance:
                        best_pair = (vehicle, client)
                        shortest_distance = possible_distance
            if best_pair[0] is not None:
                best_vehicle: Vehicle = best_pair[0]
                best_client: Place = best_pair[1]
                vehicles_id_to_places_dict[best_vehicle.vehicle_id].append(best_client)
                vehicles_id_to_current_capacity[best_vehicle.vehicle_id] -= best_client.demand
                unvisited_clients.remove(best_client)
            else:
                break

        # finishing in depot
        for vehicle in vehicles:
            route: list = vehicles_id_to_places_dict[vehicle.vehicle_id]
            if len(route) <= 1:
                vehicles_id_to_places_dict[vehicle.vehicle_id] = []
            else:
                vehicles_id_to_places_dict[vehicle.vehicle_id].append(depot)

        vehicles_id_to_places_id_dict = {}
        for vehicle_id, places_list in vehicles_id_to_places_dict.items():
            vehicles_id_to_places_id_dict[vehicle_id] = [place.place_id for place in places_list]
        solution = Solution(task, vehicles_id_to_places_id_dict)
        print("Problem Solved by greedy algorithms")
        return solution

    def solve_greedy(self):
        while (self._unvisited_clients):
            shortest_distance = float('inf')
            best_pair = (None, None)
            for vehicle in self._vehicles:
                last_place_visited_by_vehicle = vehicle.get_last_client()
                for client in self._unvisited_clients:
                    possible_distance = client.distance_to_place(last_place_visited_by_vehicle)
                    if vehicle.get_capacity() >= client.get_demand() and possible_distance < shortest_distance:
                        best_pair = (vehicle, client)
                        shortest_distance = possible_distance
            if best_pair[0] != None:
                best_vehicle = best_pair[0]
                best_client = best_pair[1]
                best_vehicle.visit_place(best_client)
                self._unvisited_clients.remove(best_client)
            else:
                break
        for vehicle in self._vehicles:
            vehicle.visit_place(self.depo)
