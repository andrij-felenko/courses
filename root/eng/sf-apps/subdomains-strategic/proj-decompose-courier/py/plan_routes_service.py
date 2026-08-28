# routing/app/plan_routes_service.py — диригент ядра. Мова предмета, не SDK.
from ..domain.route_planner import RoutePlanner, PlanRequest
from ..domain.route import Route

class PlanRoutesService:
    def __init__(self, planner: RoutePlanner):   # порт, не реалізація
        self._planner = planner

    def plan_day(self, req: PlanRequest) -> list[Route]:
        if not req.shipments:
            return []
        routes = self._planner.plan(req)
        # тут — суто наші правила поверх плану: напр. відкинути напівпорожні
        return [r for r in routes if r.fill_ratio > 0.15]
