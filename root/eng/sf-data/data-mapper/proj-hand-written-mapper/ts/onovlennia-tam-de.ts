// альтернатива до writeLines: не стирати все, а звести різницю
private async syncLines(orderId: number, lines: readonly OrderLine[]): Promise<void> {
  const current = await this.db.all<LineRow & { id: number; position: number }>(
    `SELECT id, position, sku, qty, price_cents FROM order_lines WHERE order_id = $1`,
    [orderId]);
  const have = new Map(current.map(r => [r.position, r]));

  for (const [i, l] of lines.entries()) {
    const row = have.get(i);
    have.delete(i);                                   // цю позицію розглянули

    if (!row) {
      await this.db.run(
        `INSERT INTO order_lines (order_id, position, sku, qty, price_cents)
         VALUES ($1, $2, $3, $4, $5)`, [orderId, i, l.sku, l.qty, l.price.cents]);
      continue;
    }
    if (row.sku === l.sku && row.qty === l.qty && row.price_cents === l.price.cents)
      continue;                                       // не змінилась — не чіпаємо
    await this.db.run(
      `UPDATE order_lines SET sku = $1, qty = $2, price_cents = $3 WHERE id = $4`,
      [l.sku, l.qty, l.price.cents, row.id]);
  }

  // що лишилось у have — позиції, яких в об'єкті вже нема
  for (const row of have.values())
    await this.db.run(`DELETE FROM order_lines WHERE id = $1`, [row.id]);
}
