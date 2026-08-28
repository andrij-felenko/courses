// routing/infra/GreedyPlanner.ts — той самий порт, проста реалізація.
// Для тестів ядра і для дешевого тарифу: кладемо «як влізе».
import { RoutePlanner, PlanRequest } from "../domain/RoutePlanner";
import { Route } from "../domain/Route";

export class GreedyPlanner implements RoutePlanner {
  plan(req: PlanRequest): Route[] {
    const routes = req.vehicles.map((v) => new Route(v.id, v.capacityKg));
    for (const s of req.shipments) {
      const target = routes.find((r) => r.tryAdd(s)); // у першу, куди влазить
      if (!target) throw new Error(`нікуди покласти ${s.id}`);
    }
    return routes;
  }
}
