// --- infra/ (деталь): залежить УГОРУ, від домену ---
import { Orders, Order, OrderId } from "../domain";

export class PgOrders implements Orders {        // адаптер підлаштувався під домен
  constructor(private readonly db: Pg) {}

  async save(o: Order): Promise<void> {
    await this.db.exec("insert into orders ...", o.row());
  }
  async byId(id: OrderId): Promise<Order | null> {
    const r = await this.db.query("select ... where id = $1", [id.value]);
    return r.rows.length ? Order.fromRow(r.rows[0]) : null;
  }
}
