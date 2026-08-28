# Таблиця: orders(id INTEGER PRIMARY KEY, customer_id TEXT, total REAL, status TEXT)
class Order:
    def __init__(self, customer_id: str = "", total: float = 0.0, status: str = "new"):
        self.id: int | None = None      # ключа немає → рядка ще немає
        self.customer_id = customer_id
        self.total = total
        self.status = status

    # ── знайти себе: рядок → об'єкт ──
    @classmethod
    def find(cls, id: int) -> "Order | None":
        row = db.execute(
            "SELECT customer_id, total, status FROM orders WHERE id = ?", (id,)
        ).fetchone()
        if row is None:
            return None
        order = cls(*row)
        order.id = id
        return order

    # ── зберегти себе: об'єкт → рядок ──
    def save(self) -> None:
        if self.id is None:
            cur = db.execute(
                "INSERT INTO orders (customer_id, total, status) VALUES (?, ?, ?)",
                (self.customer_id, self.total, self.status),
            )
            self.id = cur.lastrowid     # рядок народився — об'єкт запам'ятав свій ключ
        else:
            db.execute(
                "UPDATE orders SET customer_id = ?, total = ?, status = ? WHERE id = ?",
                (self.customer_id, self.total, self.status, self.id),
            )
        db.commit()

    def delete(self) -> None:
        if self.id is None:
            return
        db.execute("DELETE FROM orders WHERE id = ?", (self.id,))
        db.commit()
        self.id = None                  # ключ забрали → об'єкт знову «без рядка»

    # ── предметне правило: на тих самих даних, у тому ж класі ──
    def can_cancel(self) -> bool:
        return self.status in ("new", "paid")


order = Order.find(42)
if order and order.can_cancel():
    order.status = "cancelled"
    order.save()                        # об'єкт сам знає, що це UPDATE рядка 42
