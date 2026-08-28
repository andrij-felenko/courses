// infra/pg-orders.ts ── ЄДИНЕ місце, що знає SQL. Мапить домен ↔ рядок.
import { Order, Line } from "../domain/order";
import { Orders } from "../domain/ports";

export class PgOrders implements Orders {
  constructor(private readonly db: Pg) {}

  async save(o: Order): Promise<void> {
    await this.db.query(
      `insert into orders(id, email, lines, total) values ($1, $2, $3, $4)
       on conflict (id) do update set lines = excluded.lines, total = excluded.total`,
      [o.id, o.email, JSON.stringify(o.lines), o.total()],
    );
  }

  async byId(id: string): Promise<Order | null> {
    const r = await this.db.query("select email, lines from orders where id = $1", [id]);
    if (r.rows.length === 0) return null;
    return Order.place(id, r.rows[0].email, JSON.parse(r.rows[0].lines) as Line[]);
  }
}
