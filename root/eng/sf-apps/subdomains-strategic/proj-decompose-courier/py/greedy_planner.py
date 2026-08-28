# routing/infra/greedy_planner.py — той самий порт, проста реалізація.
# Для тестів ядра і для дешевого тарифу: кладемо «як влізе».
from ..domain.route_planner import RoutePlanner, PlanRequest
from ..domain.route import Route

class GreedyPlanner(RoutePlanner):
    def plan(self, req: PlanRequest) -> list[Route]:
        routes = [Route(v.id, v.capacity_kg) for v in req.vehicles]
        for s in req.shipments:
            placed = any(r.try_add(s) for r in routes)  # у першу, куди влазить
            if not placed:
                raise ValueError(f"нікуди покласти {s.id}")
        return routes
