class OrderMapper:
    def __init__(self, conn):          # conn.row_factory = sqlite3.Row
        self._conn = conn

    def find_by_id(self, order_id: int) -> Order | None:
        head = self._conn.execute(
            "SELECT id, placed_at, currency, status FROM orders WHERE id = ?",
            (order_id,)).fetchone()
        if head is None:
            return None

        rows = self._conn.execute(
            "SELECT sku, qty, price_cents FROM order_lines WHERE order_id = ? ORDER BY id",
            (order_id,)).fetchall()

        # збірка назад: дві таблиці → один об'єкт; копійки + код валюти → Money
        lines = [OrderLine(r["sku"], r["qty"], Money(r["price_cents"], head["currency"]))
                 for r in rows]
        return Order(head["id"], datetime.fromisoformat(head["placed_at"]),
                     lines, head["status"])

    def insert(self, order: Order) -> int:
        total = order.total()                          # Money → дві колонки
        cur = self._conn.execute(
            "INSERT INTO orders (placed_at, total_cents, currency, status) VALUES (?, ?, ?, ?)",
            (order.placed_at.isoformat(), total.cents, total.currency, order.status))
        order_id = cur.lastrowid

        self._conn.executemany(
            "INSERT INTO order_lines (order_id, sku, qty, price_cents) VALUES (?, ?, ?, ?)",
            [(order_id, l.sku, l.qty, l.price.cents) for l in order.lines])
        return order_id
