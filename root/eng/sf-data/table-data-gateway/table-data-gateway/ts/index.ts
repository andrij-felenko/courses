// Таблиця: orders(id INTEGER PRIMARY KEY, customer_id TEXT, total REAL, status TEXT)
type Row = { id: number; customer_id: string; total: number; status: string };

// Один об'єкт на всю таблицю. Тут — увесь SQL до orders і жодного правила.
class OrderTableGateway {
  // пошук: методи беруть КЛЮЧ/КРИТЕРІЙ і повертають сирі рядки (record set)
  find(id: number): Promise<Row | undefined> {
    return db.get("SELECT * FROM orders WHERE id = ?", id);
  }
  findByStatus(status: string): Promise<Row[]> {
    return db.all("SELECT * FROM orders WHERE status = ?", status);
  }

  // зміни: теж за ключем, для будь-якого рядка таблиці
  async insert(customerId: string, total: number, status: string): Promise<number> {
    const res = await db.run(
      "INSERT INTO orders (customer_id, total, status) VALUES (?, ?, ?)",
      customerId, total, status,
    );
    return res.lastID;
  }
  async update(id: number, total: number, status: string): Promise<void> {
    await db.run("UPDATE orders SET total = ?, status = ? WHERE id = ?", total, status, id);
  }
  async delete(id: number): Promise<void> {
    await db.run("DELETE FROM orders WHERE id = ?", id);
  }
}

// Виклик: правило живе ЗОВНІ, шлюз лише віддає й приймає рядки.
const gw = new OrderTableGateway();
for (const row of await gw.findByStatus("paid")) {
  if (row.total > 1000) await gw.update(row.id, row.total, "review");
}
