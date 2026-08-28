import sqlite3

db = sqlite3.connect(":memory:")
db.row_factory = sqlite3.Row


# ── ШЛЮЗ: рівно один рядок — його поля, три дієслова й прапорець наявності. ──
class OrderGateway:
    def __init__(self, customer_id, total, status="new", *, id=None, persisted=False):
        self.id = id
        self.customer_id = customer_id
        self.total = total
        self.status = status
        self.persisted = persisted          # ← чи мій рядок уже в базі

    # єдина точка запису: сам обирає INSERT чи UPDATE за прапорцем
    def save(self):
        self._update() if self.persisted else self._insert()

    def _insert(self):
        cur = db.execute(
            "INSERT INTO orders (customer_id, total, status) VALUES (?, ?, ?)",
            (self.customer_id, self.total, self.status),
        )
        self.id = cur.lastrowid             # база видала ключ
        self.persisted = True               # відтепер я в базі
        db.commit()

    def _update(self):
        db.execute(
            "UPDATE orders SET customer_id = ?, total = ?, status = ? WHERE id = ?",
            (self.customer_id, self.total, self.status, self.id),
        )
        db.commit()

    def delete(self):
        if not self.persisted:
            return
        db.execute("DELETE FROM orders WHERE id = ?", (self.id,))
        db.commit()
        self.id = None                      # ключа немає
        self.persisted = False              # рядка немає


# ── ШУКАЧ: окремий клас; виконує SELECT і будує з кожного рядка свій шлюз. ──
class OrderFinder:
    @staticmethod
    def _load(r):
        # рядок ПРИЙШОВ із бази → шлюз одразу позначено як наявний
        return OrderGateway(r["customer_id"], r["total"], r["status"],
                            id=r["id"], persisted=True)

    @staticmethod
    def find(id):
        r = db.execute("SELECT * FROM orders WHERE id = ?", (id,)).fetchone()
        return OrderFinder._load(r) if r else None

    @staticmethod
    def find_by_status(status):
        rows = db.execute("SELECT * FROM orders WHERE status = ?", (status,)).fetchall()
        return [OrderFinder._load(r) for r in rows]
