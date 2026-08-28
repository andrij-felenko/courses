// routing/app/PlanRoutesService.ts — диригент ядра. Мова предмета, не SDK.
import { RoutePlanner, PlanRequest } from "../domain/RoutePlanner";
import { Route } from "../domain/Route";

export class PlanRoutesService {
  constructor(private readonly planner: RoutePlanner) {} // порт, не реалізація

  planDay(req: PlanRequest): Route[] {
    if (req.shipments.length === 0) return [];
    const routes = this.planner.plan(req);
    // тут — суто наші правила поверх плану: напр. відкинути напівпорожні
    return routes.filter((r) => r.fillRatio > 0.15);
  }
}
