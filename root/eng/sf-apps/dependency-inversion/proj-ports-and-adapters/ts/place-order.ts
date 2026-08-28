// domain/place-order.ts ── СЦЕНАРІЙ. Диригує двома портами, не знає адаптерів.
import { Order, Line } from "./order";
import { Orders, Notifier } from "./ports";

export interface NewOrder { email: string; lines: Line[]; }

export class PlaceOrder {
  constructor(
    private readonly orders: Orders,        // ← порт, НЕ база
    private readonly notifier: Notifier,    // ← порт, НЕ SMTP
    private readonly newId: () => string,   // джерело id теж ззовні
  ) {}

  async run(cmd: NewOrder): Promise<Order> {
    const order = Order.place(this.newId(), cmd.email, cmd.lines); // 1: правила
    await this.orders.save(order);           // 2: спершу зберегти (довговічність)
    await this.notifier.orderPlaced(order);  // 3: тоді сповістити
    return order;
  }
}
