// Таблиця: orders(id INTEGER PRIMARY KEY, customer_id TEXT, total REAL, status TEXT)
type Row = { id: number; customer_id: string; total: number; status: string };

// ── ШЛЮЗ: рівно один рядок — його поля й три дієслова доступу. Правил тут немає. ──
class OrderGateway {
  constructor(
    public id: number | null,
    public customerId: string,
    public total: number,
    public status: string,
  ) {}

  async insert(): Promise<void> {
    const res = await db.run(
      "INSERT INTO orders (customer_id, total, status) VALUES (?, ?, ?)",
      this.customerId, this.total, this.status,
    );
    this.id = res.lastID;               // рядок народився — об'єкт запам'ятав ключ
  }

  async update(): Promise<void> {
    await db.run(
      "UPDATE orders SET customer_id = ?, total = ?, status = ? WHERE id = ?",
      this.customerId, this.total, this.status, this.id,
    );
  }

  async delete(): Promise<void> {
    await db.run("DELETE FROM orders WHERE id = ?", this.id);
  }
}

// ── ШУКАЧ: окремий клас; знаходить рядки й будує з них шлюзи. ──
class OrderFinder {
  static async find(id: number): Promise<OrderGateway | null> {
    const row: Row | undefined = await db.get("SELECT * FROM orders WHERE id = ?", id);
    return row ? OrderFinder.load(row) : null;
  }

  static async findByStatus(status: string): Promise<OrderGateway[]> {
    const rows: Row[] = await db.all("SELECT * FROM orders WHERE status = ?", status);
    return rows.map(OrderFinder.load);   // кожен рядок → свій шлюз
  }

  private static load(r: Row): OrderGateway {
    return new OrderGateway(r.id, r.customer_id, r.total, r.status);
  }
}
