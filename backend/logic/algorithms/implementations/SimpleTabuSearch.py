from math import inf
from operator import itemgetter

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


class CMapBuildAlgorithm:
    def __init__(self, vehicles, clients, cmap):
        self.vehicles = vehicles.copy()
        self.clients: list[Place] = clients.copy()
        self.cmap: dict = cmap

    def make_initial(self):
        s0 = [[] for _ in self.vehicles]
        visited = []
        for v_i, vehicle in enumerate(self.vehicles):
            if len(self.clients) == 0:
                break
            cap = 0
            c = random.choice(self.clients)
            s0[v_i].append(c.place_index - 1)
            visited.append(c)
            cap += c.demand
            closest = self.cmap[c.place_index]
            self.clients.remove(c)
            for distance, node in closest:
                if cap > vehicle.capacity:
                    break
                if node not in visited:
                    s0[v_i].append(node.place_index - 1)
                    visited.append(node)
                    cap += node.demand
                    self.clients.remove(node)
        return s0


class STabuSearch(Algorithm):
    max_tabu_size = 100
    TS_iter = 100
    CAP_OVERLOAD_PENALTY = 5
    use_capacity = True
    p = 20

    def __init__(self):
        super().__init__()
        self.s0 = []
        self.points = []
        self.tabu_list = set()
        self.best_cost = 0
        self.feasible = False
        self.increasing_counter = 0

    def solve(self, task: Task) -> Solution:
        self.depot: Place = task.places[0]
        self.clients: list[Place] = task.places[1:]
        self.vehicles = task.vehicles
        self.distances = task.distance_matrix

        vehicles_to_places_dict = {}

        if len(self.vehicles) == 0:
            solution = Solution(task, vehicles_to_places_dict)
            print("No vehicles!")
            return solution

        # starting from depot
        self.start_in_depo(self.depot, self.vehicles, vehicles_to_places_dict)

        # initial solution
        self.s0 = self.make_initial()

        best = self.search()

        if not self.feasible:
            best = [[] for x in self.vehicles]

        if self.feasible:
            for route, vehicle in zip(best, self.vehicles):
                for r in route:
                    place: Place = self.clients[r]
                    vehicles_to_places_dict[vehicle.vehicle_id].append(place)

        # finishing in depot
        self.finish_in_depo(self.depot, self.vehicles, vehicles_to_places_dict)

        solution = Solution(task, vehicles_to_places_dict)

        print("Problem Solved by Tabu!")
        return solution

    def make_initial(self):
        self.map_closest()
        builder = CMapBuildAlgorithm(self.vehicles, self.clients, self.cmap)
        return builder.make_initial()

    def search(self):
        s_best = self.s0
        best_candidate = self.s0
        best_global = copy(best_candidate)
        self.best_cost = 0
        i = 0
        best_fit = inf
        while not self.stopping_condition(i):
            s_neighborhood = self.neighbourhood_search(best_candidate)
            if len(s_neighborhood) == 0:
                if self.best_cost == 0:
                    self.best_cost = self.fitness(s_best)
                break
            best_moves = s_neighborhood[0]
            best_candidate = best_moves.make_move(best_candidate)
            for s_candidate_moves in s_neighborhood:
                if not s_candidate_moves.check_tabu_list(self.tabu_list):
                    s_b = s_candidate_moves.make_move(best_global)
                    if self.fitness(s_b) < self.fitness(best_candidate):
                        best_candidate = s_b
                        best_moves = s_candidate_moves

            fit = self.fitness(best_candidate)
            if fit < best_fit:
                s_best = best_candidate
                best_fit = fit
                self.increasing_counter += 1
            else:
                self.increasing_counter = 0
            best_global = copy(best_candidate)
            best_moves.update_tabu_list(self.tabu_list)
            if len(self.tabu_list) > self.max_tabu_size:
                self.tabu_list.pop()
            i += 1
        self.best_cost = best_fit
        return s_best

    def stopping_condition(self, i):
        return i > self.TS_iter and self.increasing_counter < 1

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
                if self.separation_distance(self.clients[v1],self.clients[v2]) > self.p:
                    continue
                sol = InsertMove(r1, r2, v1, i2)
                solutions.append(sol)
                sol = SwapMove(r1, r2, v1, v2, i1, i2)
                solutions.append(sol)
            sol = InsertMove(r1, r2, v1, None)
            solutions.append(sol)
        return solutions

    def separation_distance(self, client_i: Place, client_j: Place):
        return self.smap[(client_i.place_index, client_j.place_index)]

    def fitness(self, solution):
        if len(solution) == 0:
            return 0
        weight = 0
        cap_overload = 0
        for vehicle_ind, route in enumerate(solution):
            if len(route) == 0:
                continue
            u = route[0]
            weight += self.get_distance(self.depot, self.clients[u])
            for node in route[1:]:
                weight += self.get_distance(self.clients[u], self.clients[node])
                u = node
            # weight += = self.distances[self.clients[u].place_index][self.depot.place_index]
            #   ^^^ better vehicle spread if not included
            cap_overload += self.calc_capacity(route, self.vehicles[vehicle_ind].capacity)
        if cap_overload > 0:
            self.feasible = False
        else:
            self.feasible = True
        return weight + weight * cap_overload * self.CAP_OVERLOAD_PENALTY

    def calc_capacity(self, route, capacity):
        if not self.use_capacity:
            return 0
        current_capacity = 0
        for v in route:
            current_capacity += self.get_demand(v)
        if current_capacity > capacity:
            return current_capacity - capacity
        return 0

    def check_capacity_valid(self, route, capacity):
        return self.calc_capacity(route, capacity) <= 0

    def map_closest(self):
        cmap = {}
        smap = {}
        for ci in self.clients:
            p = []
            for cj in self.clients:
                if ci.place_index == cj.place_index:
                    continue
                p.append((self.get_distance(ci, cj), cj))
            p.sort(key=itemgetter(0))
            for i, (d, cj) in enumerate(p):
                smap.update({(ci.place_index,cj.place_index): i})
            cmap.update({ci.place_index: p})
        self.cmap = cmap
        self.smap = smap

    def get_demand(self, v):
        return self.clients[v].demand

    def get_distance(self, place_u, place_v) -> int:
        return self.distances[place_u.place_index][place_v.place_index]

