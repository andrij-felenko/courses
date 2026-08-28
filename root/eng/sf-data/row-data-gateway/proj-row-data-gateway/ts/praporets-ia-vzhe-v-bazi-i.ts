import { DatabaseSync } from "node:sqlite";

const db = new DatabaseSync(":memory:");
type Row = { id: number; customer_id: string; total: number; status: string };

// ── ШЛЮЗ: рівно один рядок — його поля, три дієслова й прапорець наявності. ──
class OrderGateway {
  id: number | null;
  persisted: boolean;                        // ← чи мій рядок уже в базі

  constructor(
    public customerId: string,
    public total: number,
    public status = "new",
    init: { id?: number; persisted?: boolean } = {},
  ) {
    this.id = init.id ?? null;
    this.persisted = init.persisted ?? false;
  }

  // єдина точка запису: сам обирає INSERT чи UPDATE за прапорцем
  save(): void {
    if (this.persisted) this.update();
    else this.insert();
  }

  private insert(): void {
    const info = db
      .prepare("INSERT INTO orders (customer_id, total, status) VALUES (?, ?, ?)")
      .run(this.customerId, this.total, this.status);
    this.id = Number(info.lastInsertRowid);  // база видала ключ
    this.persisted = true;                   // відтепер я в базі
  }                                          // node:sqlite фіксує кожен .run() сам

  private update(): void {
    db.prepare("UPDATE orders SET customer_id = ?, total = ?, status = ? WHERE id = ?")
      .run(this.customerId, this.total, this.status, this.id);
  }

  delete(): void {
    if (!this.persisted) return;
    db.prepare("DELETE FROM orders WHERE id = ?").run(this.id);
    this.id = null;                          // ключа немає
    this.persisted = false;                  // рядка немає
  }
}

// ── ШУКАЧ: окремий клас; виконує SELECT і будує з кожного рядка свій шлюз. ──
class OrderFinder {
  // рядок ПРИЙШОВ із бази → шлюз одразу позначено як наявний
  private static load(r: Row): OrderGateway {
    return new OrderGateway(r.customer_id, r.total, r.status,
                            { id: r.id, persisted: true });
  }

  static find(id: number): OrderGateway | null {
    const r = db.prepare("SELECT * FROM orders WHERE id = ?").get(id) as Row | undefined;
    return r ? OrderFinder.load(r) : null;
  }

  static findByStatus(status: string): OrderGateway[] {
    const rows = db.prepare("SELECT * FROM orders WHERE status = ?").all(status) as Row[];
    return rows.map((r) => OrderFinder.load(r));
  }
}
