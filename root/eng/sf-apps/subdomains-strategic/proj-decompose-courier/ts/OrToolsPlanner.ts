// routing/infra/OrToolsPlanner.ts — АДАПТЕР + ACL.
// Єдине місце, де живе мова чужого розв'язувача.
import { RoutePlanner, PlanRequest } from "../domain/RoutePlanner";
import { Route, Shipment } from "../domain/Route";
import { solveVrp } from "some-or-tools-binding"; // чужий SDK — лише тут

export class OrToolsPlanner implements RoutePlanner {
  plan(req: PlanRequest): Route[] {
    // 1) НАШЕ → ЧУЖЕ: перекладаємо відправлення в матрицю індексів
    const nodes = req.shipments.map((s, i) => ({ index: i, addr: s.address }));
    const distance = this.buildDistanceMatrix(nodes);      // їхня «розмірність»
    const demands = req.shipments.map((s) => s.weightKg);  // їхній колбек попиту
    const caps = req.vehicles.map((v) => v.capacityKg);

    // 2) кличемо чужий двигун — тут його мова індексів і матриць
    const raw = solveVrp({ distance, demands, capacities: caps });

    // 3) ЧУЖЕ → НАШЕ: індекси вузлів назад у Route з наших Shipment
    return raw.routes.map((r, k) => {
      const route = new Route(req.vehicles[k].id, caps[k]);
      for (const nodeIndex of r.stops) {
        route.tryAdd(req.shipments[nodeIndex]);   // назад у наші поняття
      }
      return route;
    });
  }

  private buildDistanceMatrix(nodes: { addr: string }[]): number[][] {
    // тут була б геокодизація/матриця відстаней; деталь чужого світу
    return nodes.map(() => nodes.map(() => 0));
  }
}
