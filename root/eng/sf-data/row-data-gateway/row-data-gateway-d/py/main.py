# Таблиця: orders(id INTEGER PRIMARY KEY, customer_id TEXT, total REAL, status TEXT)

# ── ШЛЮЗ: рівно один рядок — його поля й три дієслова доступу. Правил тут немає. ──
class OrderGateway:
    def __init__(self, id, customer_id, total, status):
        self.id = id                    # None → рядка ще немає
        self.customer_id = customer_id
        self.total = total
        self.status = status

    def insert(self):
        cur = db.execute(
            "INSERT INTO orders (customer_id, total, status) VALUES (?, ?, ?)",
            (self.customer_id, self.total, self.status),
        )
        self.id = cur.lastrowid         # рядок народився — об'єкт запам'ятав ключ

    def update(self):
        db.execute(
            "UPDATE orders SET customer_id = ?, total = ?, status = ? WHERE id = ?",
            (self.customer_id, self.total, self.status, self.id),
        )

    def delete(self):
        db.execute("DELETE FROM orders WHERE id = ?", (self.id,))


# ── ШУКАЧ: окремий клас; знаходить рядки й будує з них шлюзи. ──
class OrderFinder:
    @staticmethod
    def find(id):
        row = db.execute("SELECT * FROM orders WHERE id = ?", (id,)).fetchone()
        return OrderFinder._load(row) if row else None

    @staticmethod
    def find_by_status(status):
        rows = db.execute("SELECT * FROM orders WHERE status = ?", (status,)).fetchall()
        return [OrderFinder._load(r) for r in rows]   # кожен рядок → свій шлюз

    @staticmethod
    def _load(r):
        return OrderGateway(r["id"], r["customer_id"], r["total"], r["status"])
