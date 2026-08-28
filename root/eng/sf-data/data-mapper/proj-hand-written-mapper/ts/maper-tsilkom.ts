type Status = "new" | "shipped" | "cancelled";
type HeadRow = { id: number; placed_at: string; currency: string; status: Status };
type LineRow = { sku: string; qty: number; price_cents: number };

class OrderMapper {
  constructor(private readonly db: Executor) {}      // не Pool — конкретне з'єднання

  async findById(id: number): Promise<Order | null> {
    const head = await this.db.one<HeadRow>(
      `SELECT id, placed_at, currency, status FROM orders WHERE id = $1`, [id]);
    if (!head) return null;

    const rows = await this.db.all<LineRow>(
      `SELECT sku, qty, price_cents FROM order_lines
       WHERE order_id = $1 ORDER BY position`, [id]);
    return this.build(head, rows);
  }

  async findByStatus(status: Status): Promise<Order[]> {
    const heads = await this.db.all<HeadRow>(
      `SELECT id, placed_at, currency, status FROM orders WHERE status = $1`, [status]);
    if (heads.length === 0) return [];

    // ОДИН запит на всі позиції — не по запиту на кожне замовлення
    const rows = await this.db.all<LineRow & { order_id: number }>(
      `SELECT order_id, sku, qty, price_cents FROM order_lines
       WHERE order_id = ANY($1) ORDER BY order_id, position`, [heads.map(h => h.id)]);

    const byOrder = new Map<number, LineRow[]>();
    for (const r of rows) {
      const bucket = byOrder.get(r.order_id);
      if (bucket) bucket.push(r); else byOrder.set(r.order_id, [r]);
    }
    return heads.map(h => this.build(h, byOrder.get(h.id) ?? []));
  }

  async insert(order: Order): Promise<Order> {
    const total = order.total();
    const head = await this.db.one<{ id: number }>(
      `INSERT INTO orders (placed_at, total_cents, currency, status)
       VALUES ($1, $2, $3, $4) RETURNING id`,
      [order.placedAt, total.cents, total.currency, order.state]);

    await this.writeLines(head!.id, order.lines);
    // id readonly — вписати його в переданий об'єкт не можна, тож віддаємо новий
    return new Order(head!.id, order.placedAt, order.lines, order.state);
  }

  async update(order: Order): Promise<void> {
    const id = this.identified(order);
    const total = order.total();
    const { rowCount } = await this.db.run(
      `UPDATE orders SET placed_at = $1, total_cents = $2, currency = $3, status = $4
       WHERE id = $5`,
      [order.placedAt, total.cents, total.currency, order.state, id]);

    if (rowCount === 0) throw new Error(`orders#${id}: рядка нема — його встигли видалити?`);

    await this.db.run(`DELETE FROM order_lines WHERE order_id = $1`, [id]);
    await this.writeLines(id, order.lines);
  }

  async delete(order: Order): Promise<void> {
    const id = this.identified(order);
    await this.db.run(`DELETE FROM order_lines WHERE order_id = $1`, [id]);  // явно, не каскадом
    const { rowCount } = await this.db.run(`DELETE FROM orders WHERE id = $1`, [id]);
    if (rowCount === 0) throw new Error(`orders#${id}: видаляти нема чого`);
  }

  // ── внутрішнє ──────────────────────────────────────────────────────────
  private build(head: HeadRow, rows: LineRow[]): Order {
    if (rows.length === 0)
      throw new Error(`orders#${head.id}: голова є, позицій нема — база суперечить домену`);
    const lines = rows.map(r =>
      new OrderLine(r.sku, r.qty, new Money(r.price_cents, head.currency)));
    return new Order(head.id, new Date(head.placed_at), lines, head.status);
  }

  private async writeLines(orderId: number, lines: readonly OrderLine[]): Promise<void> {
    for (const [i, l] of lines.entries())
      await this.db.run(
        `INSERT INTO order_lines (order_id, position, sku, qty, price_cents)
         VALUES ($1, $2, $3, $4, $5)`, [orderId, i, l.sku, l.qty, l.price.cents]);
  }

  private identified(order: Order): number {
    if (order.id === null) throw new Error("об'єкт без id: спершу insert");
    return order.id;
  }
}
