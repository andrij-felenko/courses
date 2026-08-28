// infra/in-memory.ts ── адаптери БЕЗ інфраструктури. Реалізують ті самі порти.
import { Order } from "../domain/order";
import { Orders, Notifier } from "../domain/ports";

export class InMemoryOrders implements Orders {
  private byKey = new Map<string, Order>();
  async save(o: Order): Promise<void> { this.byKey.set(o.id, o); }
  async byId(id: string): Promise<Order | null> { return this.byKey.get(id) ?? null; }
}

// Шпигун: не «нічого не робить», а ЗАПИСУЄ, кого сповістили.
export class InMemoryNotifier implements Notifier {
  readonly sent: Order[] = [];
  async orderPlaced(o: Order): Promise<void> { this.sent.push(o); }
}
