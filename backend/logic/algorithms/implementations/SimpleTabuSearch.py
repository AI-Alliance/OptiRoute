from math import inf
from logic import Task
from logic.models.Place import Place
from logic.Solution import Solution
from logic.algorithms.Algorithm import Algorithm

from logic.algorithms.utils import IterPairs, copy_refs, DistanceMapper, CMapBuildAlgorithm, hash_solution


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
        routes = copy_refs(solution)
        if self.position is None:
            routes[self.to_route].append(self.value)
        else:
            routes[self.to_route].insert(self.position, self.value)
        routes[self.from_route].remove(self.value)
        return routes

    # def update_tabu_list(self, tabu_list: set):
    #     tabu_list.add((self.from_route, self.value))
    #
    # def check_tabu_list(self, tabu_list):
    #     return (self.to_route, self.value) in tabu_list


class SwapMove(Move):
    def __init__(self, route1, route2, value1, value2, position1, position2):
        self.route1 = route1
        self.route2 = route2
        self.value1 = value1
        self.value2 = value2
        self.position1 = position1
        self.position2 = position2

    def make_move(self, solution) -> list:
        routes = copy_refs(solution)
        routes[self.route1][self.position1] = self.value2
        routes[self.route2][self.position2] = self.value1
        return routes

    # def update_tabu_list(self, tabu_list: set):
    #     tabu_list.add((self.route1, self.value1))
    #     tabu_list.add((self.route2, self.value2))
    #
    # def check_tabu_list(self, tabu_list):
    #     return ((self.route2, self.value1) in tabu_list
    #             and (self.route1, self.value2) in tabu_list)



def update_tabu(move: Move, tabu_list, solution):
    # move.update_tabu_list(tabu_list)
    tabu_list.add(hash_solution(solution))
    return tabu_list

def is_in_tabu(move: Move, tabu_list, solution):
    return hash_solution(solution) in tabu_list
    # return move.check_tabu_list(tabu_list)


class STabuSearch(Algorithm):
    USE_LIMITING_TABU = False
    MAX_TABU_SIZE = 0 #^
    TS_iter = 100
    CAP_OVERLOAD_PENALTY = 5
    use_capacity = True
    USE_LIMITING_NEIGHBOURHOOD = True
    p = 20 # limit neighbourhood to p-closest

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
        self.dm = DistanceMapper(self.clients, self.distances)
        self.cmap, self.smap = self.dm.map_closest()
        self.s0 = self.make_initial()

        # calculate solution
        best = self.search()
        if not self.feasible:
            return Solution(task, {})
            # best = [[] for _ in self.vehicles]

        for route, vehicle in zip(best, self.vehicles):
            for r in route:
                place: Place = self.clients[r]
                vehicles_to_places_dict[vehicle.vehicle_id].append(place)

        # finishing in depot
        self.finish_in_depo(self.depot, self.vehicles, vehicles_to_places_dict)

        solution = Solution(task, vehicles_to_places_dict)

        print("Problem Solved by Tabu!")
        return solution

    def outside_solve_init(self, task):
        self.depot: Place = task.places[0]
        self.clients: list[Place] = task.places[1:]
        self.vehicles = task.vehicles
        self.distances = task.distance_matrix
        self.dm = DistanceMapper(self.clients, self.distances)
        self.cmap, self.smap = self.dm.map_closest()

    def outside_solve(self, initial):
        self.s0 = initial
        best = self.search()
        return best

    def make_initial(self):
        build_algo = CMapBuildAlgorithm(self.vehicles, self.clients, self.cmap)
        return build_algo.make_initial()

    def search(self):
        s_best = self.s0 # best solution
        s_best_fit = self.fitness(s_best) # best solution cost
        i = 0 # iteration counter
        self.increasing_counter = 0
        ref = self.s0 # previous best candidate sol

        while not self.stopping_condition(i): # iterations
            s_neighborhood = self.neighbourhood_search(ref)
            if len(s_neighborhood) == 0:
                break
            best_candidate_moves = s_neighborhood[0] # best from neighbourhood
            best_candidate_sol = best_candidate_moves.make_move(ref)
            best_candidate_fit = self.fitness(best_candidate_sol)
            for candidate_moves in s_neighborhood: # find best from neighbourhood
                if not is_in_tabu(candidate_moves, self.tabu_list, candidate_moves.make_move(ref)):
                    candidate_sol = candidate_moves.make_move(ref)
                    if self.fitness(candidate_sol) < best_candidate_fit:
                        best_candidate_sol = candidate_sol
                        best_candidate_moves = candidate_moves
                        best_candidate_fit = self.fitness(best_candidate_sol)
            self.tabu_list = update_tabu(best_candidate_moves, self.tabu_list, best_candidate_sol) # update tabu list with best from neighbourhood
            if best_candidate_fit < s_best_fit: # new best (if it is better)
                s_best = best_candidate_sol
                s_best_fit = best_candidate_fit
                self.feasible = self.check_feasibility(s_best)
                self.increasing_counter = 10
            elif self.increasing_counter > 0:
                self.increasing_counter -= 1
            ref = best_candidate_sol

            if self.USE_LIMITING_TABU and len(self.tabu_list) > self.MAX_TABU_SIZE:
                for i in range(self.MAX_TABU_SIZE // 10):
                    self.tabu_list.pop()
            i += 1
        return s_best

    def stopping_condition(self, i):
        if i > self.TS_iter and self.increasing_counter > 0:
            self.TS_iter += 10
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
                if self.USE_LIMITING_NEIGHBOURHOOD and self.separation_distance(self.clients[v1],self.clients[v2]) > self.p:
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
            weight += self.get_distance(self.clients[u], self.depot)
            cap_overload += self.calc_capacity(route, self.vehicles[vehicle_ind].capacity)
        return weight + weight * cap_overload * self.CAP_OVERLOAD_PENALTY

    def check_feasibility(self, solution):
        cap_overload = 0
        for vehicle_ind, route in enumerate(solution):
            cap_overload += self.calc_capacity(route, self.vehicles[vehicle_ind].capacity)
        if cap_overload > 0:
            return False
        else:
            return True

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

    def get_demand(self, v):
        return self.clients[v].demand

    def get_distance(self, place_u, place_v) -> int:
        return self.distances[place_u.place_index][place_v.place_index]

