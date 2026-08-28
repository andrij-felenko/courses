class OrderMapper {
  constructor(private readonly db: Db) {}

  async findById(id: number): Promise<Order | null> {
    const head = await this.db.one(
      `SELECT id, placed_at, currency, status FROM orders WHERE id = $1`, [id]);
    if (!head) return null;

    const rows = await this.db.all(
      `SELECT sku, qty, price_cents FROM order_lines WHERE order_id = $1 ORDER BY id`, [id]);

    // збірка назад: дві таблиці → один об'єкт; копійки + код валюти → Money
    const lines = rows.map(r => new OrderLine(r.sku, r.qty, new Money(r.price_cents, head.currency)));
    return new Order(head.id, new Date(head.placed_at), lines, head.status);
  }

  async insert(order: Order): Promise<number> {
    const total = order.total();                        // Money → дві колонки
    const { id } = await this.db.one(
      `INSERT INTO orders (placed_at, total_cents, currency, status)
       VALUES ($1, $2, $3, $4) RETURNING id`,
      [order.placedAt, total.cents, total.currency, order.state]);

    for (const l of order.lines) {
      await this.db.run(
        `INSERT INTO order_lines (order_id, sku, qty, price_cents) VALUES ($1, $2, $3, $4)`,
        [id, l.sku, l.qty, l.price.cents]);
    }
    return id;
  }
}
