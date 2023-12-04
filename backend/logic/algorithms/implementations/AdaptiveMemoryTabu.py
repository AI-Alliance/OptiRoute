from logic import Task
from logic.models.Place import Place
from logic.Solution import Solution
from logic.algorithms.Algorithm import Algorithm
from logic.algorithms.implementations import STabuSearch

from logic.algorithms.utils import IterPairs, copy_refs, DistanceMapper, CMapBuildAlgorithm
from operator import attrgetter, itemgetter
import random

class RouteWithLabel:
    def __init__(self, feasibility, cost, route):
        self.feasibility = feasibility
        self.cost = cost
        self.route = route

    def __repr__(self):
        return repr((self.feasibility, self.cost, self.route))


def select_in_m(m: list):
    n = random.random()
    size = len(m)
    c = 0
    for i in range(size):
        c += 2 * (size + 1 - (i + 1)) / (size * (size + 1))
        if n <= c:
            return m[i]
    return m[size - 1]


def insert_sorted_labeled_routes(a: list[RouteWithLabel], x: RouteWithLabel):
    i = 0
    while i < len(a):
        if a[i].feasibility < x.feasibility:
            break
        elif a[i].feasibility == x.feasibility and a[i].cost < x.cost:
            break
        i += 1
    a.insert(i, x)


class AdaptiveMemoryTabuSearch(Algorithm):
    AMP_iter = 20  # number of AMP iterations
    I = 4 # number of initial solution in Memory
    use_capacity = True
    CAP_OVERLOAD_PENALTY = 5
    USE_INITIAL_TABU_SEARCH = False

    def __init__(self):
        super().__init__()
        self.VehMemory = None
        self.feasible = False

    def solve(self, task: Task) -> Solution:
        self.depot: Place = task.places[0]
        self.clients: list[Place] = task.places[1:]
        self.vehicles = task.vehicles
        self.distances = task.distance_matrix
        # self.client_ids =
        self.VehMemory: list[list[RouteWithLabel]] = [[] for _ in self.vehicles]
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
        self.TS = STabuSearch()
        self.TS.outside_solve_init(task)
        self.initial()

        # calculate solution
        best = self.search()

        if not self.feasible:
            best = [[] for x in self.vehicles]

        for route, vehicle in zip(best, self.vehicles):
            for r in route:
                place: Place = self.clients[r]
                vehicles_to_places_dict[vehicle.vehicle_id].append(place)

        # finishing in depot
        self.finish_in_depo(self.depot, self.vehicles, vehicles_to_places_dict)

        solution = Solution(task, vehicles_to_places_dict)
        print("Problem Solved by Tabu!")
        return solution

    def initial(self):
        build_algo = CMapBuildAlgorithm(self.vehicles, self.clients, self.cmap)
        for i in range(self.I):
            s = build_algo.make_initial()
            if self.USE_INITIAL_TABU_SEARCH:
                s = self.TS.outside_solve(s)
            self.add_to_memory(s)

    def add_to_memory(self, s):
        f = self.check_feasibility(s)
        c = -self.check_cost(s)
        for i, r in enumerate(s):
            insert_sorted_labeled_routes(self.VehMemory[i], RouteWithLabel(f, c, r))

    def check_cost(self, solution):
        if len(solution) == 0:
            return 0
        weight = 0
        for vehicle_ind, route in enumerate(solution):
            if len(route) == 0:
                continue
            u = route[0]
            weight += self.get_distance(self.depot, self.clients[u])
            for node in route[1:]:
                weight += self.get_distance(self.clients[u], self.clients[node])
                u = node
            weight += self.get_distance(self.clients[u], self.depot)
        return weight

    def check_feasibility(self, solution):
        cap_overload = 0
        for vehicle_ind, route in enumerate(solution):
            cap_overload += self.calc_capacity(route, self.vehicles[vehicle_ind].capacity)
        if cap_overload > 0:
            return 0
        else:
            return 1

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

    def whip_existing(self, m, r: RouteWithLabel):
        for i, vm2 in enumerate(m):  # for every vehicle
            del_list = []
            for lr_i, labeled_route in enumerate(vm2):  # for it's labeled routes in memory
                if any(x in r.route for x in labeled_route.route):
                    del_list.append(labeled_route)
            m[i] = [x for x in vm2 if x not in del_list]
        return m

    def construct_solution(self):
        m_prim = copy_refs(self.VehMemory)
        unrouted_clients = [c.place_index - 1 for c in self.clients]
        solution = [[] for _ in self.vehicles]
        capacities = [0 for v in self.vehicles]
        v_i = 0
        while v_i < len(m_prim):
            vm = m_prim[v_i]
            r = select_in_m(vm)
            solution[v_i] = r.route
            capacities[v_i] += r.cost
            for c in r.route:
                unrouted_clients.remove(c)
            m_prim = self.whip_existing(m_prim, r)
            v_i += 1

        if len(unrouted_clients) > 0:
            for c in unrouted_clients:
                ki = -1
                dem = 0
                for i, r in enumerate(solution):
                    dem = self.clients[c].demand
                    if capacities[i] + dem <= self.vehicles[i].capacity:
                        ki = i
                        break
                solution[ki].append(c)
                capacities[ki] += dem
        return solution

    def search(self):
        best_sol_global = []
        best_fit_global = 0
        best_feasibility = 0
        for i in range(self.AMP_iter):
            s = self.construct_solution()
            bs = self.TS.outside_solve(s)
            bc = self.fitness(bs)
            bf = self.check_feasibility(bs)
            if best_fit_global == 0 or bf > best_feasibility or bc < best_fit_global:
                best_sol_global = bs
                best_fit_global = bc
                best_feasibility = bf
                self.feasible = best_feasibility == 1
            self.add_to_memory(bs)
        return best_sol_global
