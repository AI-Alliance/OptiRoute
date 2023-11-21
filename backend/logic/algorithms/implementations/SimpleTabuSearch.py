
from logic import Task
from logic.models.Place import Place
from logic.Solution import Solution
from logic.algorithms.Algorithm import Algorithm

from logic.algorithms.utils import IterPairs, copy
import random

class Move:
    def make_move(self, routes) -> list:
        pass

    def update_tabu_list(self, tabu_list: set):
        pass

    def check_tabu_list(self, tabu_list) -> bool:
        pass


class InsertMove(Move):
    def __init__(self, from_route, to_route, value, position):
        self.from_route = from_route
        self.to_route = to_route
        self.value = value
        self.position = position

    def make_move(self, solution) -> list:
        routes = copy(solution)
        if self.position is None:
            routes[self.to_route].append(self.value)
        else:
            routes[self.to_route].insert(self.position, self.value)
        routes[self.from_route].remove(self.value)
        return routes

    def update_tabu_list(self, tabu_list: set):
        tabu_list.add((self.from_route, self.value))

    def check_tabu_list(self, tabu_list):
        return (self.to_route, self.value) in tabu_list

    def calculate_cost(self, solution, cost):
        pass


class SwapMove(Move):
    def __init__(self, route1, route2, value1, value2, position1, position2):
        self.route1 = route1
        self.route2 = route2
        self.value1 = value1
        self.value2 = value2
        self.position1 = position1
        self.position2 = position2

    def make_move(self, solution) -> list:
        routes = copy(solution)
        routes[self.route1][self.position1] = self.value2
        routes[self.route2][self.position2] = self.value1
        return routes

    def update_tabu_list(self, tabu_list: set):
        tabu_list.add((self.route1, self.value1))
        tabu_list.add((self.route2, self.value2))

    def check_tabu_list(self, tabu_list):
        return ((self.route2, self.value1) in tabu_list
                and (self.route1, self.value2) in tabu_list)


class STabuSearch(Algorithm):
    TS_iter = 50
    CAP_OVERLOAD_PENALTY = 5
    use_capacity = True

    def __init__(self):
        super().__init__()
        self.s0 = []
        self.points = []
        self.max_tabu_size = 100
        self.tabu_list = set()
        self.p = 5  # TODO limit neighbourhood to p-closest
        self.best_cost = 0


    def solve(self, task: Task) -> Solution:
        self.depot: Place = task.places[0]
        self.clients = task.places[1:]
        self.vehicles = task.vehicles
        self.distances = task.distance_matrix

        vehicles_to_places_dict = {}

        if len(self.vehicles) == 0:
            solution = Solution(task, vehicles_to_places_dict)
            print("No vehicles!")
            return solution

        # starting from depot
        for vehicle in self.vehicles:
            vehicles_to_places_dict[vehicle.vehicle_id] = [self.depot]

        # initial solution
        self.s0 = [[] for x in self.vehicles]
        for client in self.clients:
            v_i = random.randint(0, len(self.vehicles)-1)
            self.s0[v_i].append(client.place_index-1)

        best = self.search()
        for route, vehicle in zip(best, self.vehicles):
            for r in route:
                place: Place = self.clients[r]
                vehicles_to_places_dict[vehicle.vehicle_id].append(place)

        # finishing in depot
        for vehicle in self.vehicles:
            vehicles_to_places_dict[vehicle.vehicle_id].append(self.depot)

        vehicles_id_to_places_id_dict = {}
        for vehicle_id, places_list in vehicles_to_places_dict.items():
            vehicles_id_to_places_id_dict[vehicle_id] = [place.place_id for place in places_list]
        solution = Solution(task, vehicles_id_to_places_id_dict)

        print("Problem Solved by Tabu!")
        return solution

    def search(self):
        s_best = self.s0
        best_candidate = self.s0
        best_global = copy(best_candidate)
        self.best_cost = 0
        i = 0
        best_fit = 0
        while not self.stopping_condition(i):
            s_neighborhood = self.neighbourhood_search(best_candidate)
            if len(s_neighborhood) == 0:
                if self.best_cost == 0:
                    self.best_cost = -self.fitness(s_best)
                break
            best_moves = s_neighborhood[0]
            best_candidate = best_moves.make_move(best_candidate)
            for s_candidate_moves in s_neighborhood:
                if not s_candidate_moves.check_tabu_list(self.tabu_list):
                    s_b = s_candidate_moves.make_move(best_global)
                    if self.fitness(s_b) > self.fitness(best_candidate):
                        best_candidate = s_b
                        best_moves = s_candidate_moves

            if self.fitness(best_candidate) > self.fitness(s_best):
                s_best = best_candidate
            best_global = copy(best_candidate)
            best_moves.update_tabu_list(self.tabu_list)
            if len(self.tabu_list) > self.max_tabu_size:
                self.tabu_list.pop()
            i += 1
            best_fit = self.fitness(s_best)
            if i % 10 == 0:
                print(f"TS {i}/{self.TS_iter} current best: {-best_fit}")
        self.best_cost = -best_fit
        return s_best

    def stopping_condition(self, i):
        return i > self.TS_iter

    def neighbourhood_search(self, routes: list) -> list[Move]:
        all_solutions = []
        for route1, route2 in IterPairs(len(routes)):
            if route1 == route2:
                continue
            solutions = self.two_lists_exchanges(routes, route1, route2)
            all_solutions += solutions
        return all_solutions

    def two_lists_exchanges(self, routes: list, r1: int, r2: int) -> list[Move]:
        solutions = []
        for i1, v1 in enumerate(routes[r1]):
            for i2, v2 in enumerate(routes[r2]):
                sol = InsertMove(r1, r2, v1, i2)
                solutions.append(sol)
                sol = SwapMove(r1, r2, v1, v2, i1, i2)
                solutions.append(sol)  # comment it if slow
            sol = InsertMove(r1, r2, v1, None)
            solutions.append(sol)
        return solutions

    def fitness(self, solution):
        if len(solution) == 0:
            return 0
        weight = 0
        cap_overload = 0
        for vehicle_ind, route in enumerate(solution):
            if len(route) == 0:
                continue
            u = route[0]
            weight += self.distances[self.depot.place_index][self.clients[u].place_index]
            for node in route[1:]:
                weight += self.distances[self.clients[u].place_index][self.clients[node].place_index]
                u = node
            # weight += = self.distances[self.clients[u].place_index][self.depot.place_index]
            #   ^^^ better vehicle spread if commented
            cap_overload += self.calc_capacity(route, self.vehicles[vehicle_ind].capacity)
        return - (weight + weight * cap_overload * self.CAP_OVERLOAD_PENALTY)

    def calc_capacity(self, route, capacity):
        if not self.use_capacity:
            return 0
        current_capacity = 0
        for v in route:
            current_capacity += self.get_demand(v)
        if current_capacity > capacity:
            return current_capacity - capacity
        return 0

    # def check_capacity_valid(self, route, capacity):
    #     return self.calc_capacity(route, capacity) <= 0


    def get_demand(self, v):
        return self.clients[v].demand

