// Таблиця: orders(id INTEGER PRIMARY KEY, customer_id TEXT, total REAL, status TEXT)
type Row = { id: number; customer_id: string; total: number; status: string };

class Order {
  id: number | null = null;      // ключа немає → рядка ще немає
  customerId = "";
  total = 0;
  status = "new";

  // ── знайти себе: рядок → об'єкт ──
  static async find(id: number): Promise<Order | null> {
    const row: Row | undefined = await db.get("SELECT * FROM orders WHERE id = ?", id);
    if (!row) return null;
    const o = new Order();
    o.id = row.id;
    o.customerId = row.customer_id;
    o.total = row.total;
    o.status = row.status;
    return o;
  }

  // ── зберегти себе: об'єкт → рядок ──
  async save(): Promise<void> {
    if (this.id === null) {
      const res = await db.run(
        "INSERT INTO orders (customer_id, total, status) VALUES (?, ?, ?)",
        this.customerId, this.total, this.status,
      );
      this.id = res.lastID;      // рядок народився — об'єкт запам'ятав свій ключ
    } else {
      await db.run(
        "UPDATE orders SET customer_id = ?, total = ?, status = ? WHERE id = ?",
        this.customerId, this.total, this.status, this.id,
      );
    }
  }

  async delete(): Promise<void> {
    if (this.id === null) return;
    await db.run("DELETE FROM orders WHERE id = ?", this.id);
    this.id = null;              // ключ забрали → об'єкт знову «без рядка»
  }

  // ── предметне правило: на тих самих даних, у тому ж класі ──
  canCancel(): boolean {
    return this.status === "new" || this.status === "paid";
  }
}

const order = await Order.find(42);
if (order?.canCancel()) {
  order.status = "cancelled";
  await order.save();            // об'єкт сам знає, що це UPDATE рядка 42
}
