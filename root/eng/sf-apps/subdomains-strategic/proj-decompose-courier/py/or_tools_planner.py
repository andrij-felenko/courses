# routing/infra/or_tools_planner.py — АДАПТЕР + ACL.
# Єдине місце, де живе мова чужого розв'язувача.
from ..domain.route_planner import RoutePlanner, PlanRequest
from ..domain.route import Route
from some_or_tools_binding import solve_vrp   # чужий SDK — лише тут

class OrToolsPlanner(RoutePlanner):
    def plan(self, req: PlanRequest) -> list[Route]:
        # 1) НАШЕ → ЧУЖЕ: відправлення в матрицю індексів
        nodes = list(enumerate(s.address for s in req.shipments))
        distance = self._build_distance_matrix(nodes)     # їхня «розмірність»
        demands = [s.weight_kg for s in req.shipments]    # їхній колбек попиту
        caps = [v.capacity_kg for v in req.vehicles]

        # 2) кличемо чужий двигун — тут його мова індексів і матриць
        raw = solve_vrp(distance=distance, demands=demands, capacities=caps)

        # 3) ЧУЖЕ → НАШЕ: індекси вузлів назад у Route з наших Shipment
        routes: list[Route] = []
        for k, r in enumerate(raw.routes):
            route = Route(req.vehicles[k].id, caps[k])
            for node_index in r.stops:
                route.try_add(req.shipments[node_index])  # назад у наші поняття
            routes.append(route)
        return routes

    def _build_distance_matrix(self, nodes) -> list[list[float]]:
        # тут була б геокодизація/матриця відстаней; деталь чужого світу
        return [[0.0 for _ in nodes] for _ in nodes]
