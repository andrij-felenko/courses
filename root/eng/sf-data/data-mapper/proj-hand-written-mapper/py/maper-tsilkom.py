import sqlite3
from contextlib import contextmanager
from datetime import datetime


def connect(path):
    conn = sqlite3.connect(path, isolation_level=None)   # BEGIN пишемо самі
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")             # інакше REFERENCES — просто напис
    return conn


@contextmanager
def transaction(conn):
    """Межу задає той, хто кличе, — не мапер."""
    conn.execute("BEGIN")
    try:
        yield conn
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise


class OrderMapper:
    def __init__(self, conn):                            # конкретне з'єднання, не пул
        self._conn = conn

    def find_by_id(self, order_id):
        head = self._conn.execute(
            "SELECT id, placed_at, currency, status FROM orders WHERE id = ?",
            (order_id,)).fetchone()
        if head is None:
            return None

        rows = self._conn.execute(
            "SELECT sku, qty, price_cents FROM order_lines "
            "WHERE order_id = ? ORDER BY position", (order_id,)).fetchall()
        return self._build(head, rows)

    def find_by_status(self, status):
        heads = self._conn.execute(
            "SELECT id, placed_at, currency, status FROM orders WHERE status = ?",
            (status,)).fetchall()
        if not heads:
            return []

        ids = [h["id"] for h in heads]
        holes = ",".join("?" * len(ids))                  # IN (?,?,?) — за кількістю id
        rows = self._conn.execute(                        # ОДИН запит на всі позиції
            "SELECT order_id, sku, qty, price_cents FROM order_lines "
            f"WHERE order_id IN ({holes}) ORDER BY order_id, position", ids).fetchall()

        by_order = {}
        for r in rows:
            by_order.setdefault(r["order_id"], []).append(r)
        return [self._build(h, by_order.get(h["id"], [])) for h in heads]

    def insert(self, order):
        total = order.total()
        cur = self._conn.execute(
            "INSERT INTO orders (placed_at, total_cents, currency, status) "
            "VALUES (?, ?, ?, ?)",
            (order.placed_at.isoformat(), total.cents, total.currency, order.status))

        order.id = cur.lastrowid          # поле відкрите — мапер вписує тотожність на місці
        self._write_lines(order.id, order.lines)
        return order

    def update(self, order):
        order_id = self._identified(order)
        total = order.total()
        cur = self._conn.execute(
            "UPDATE orders SET placed_at = ?, total_cents = ?, currency = ?, status = ? "
            "WHERE id = ?",
            (order.placed_at.isoformat(), total.cents, total.currency,
             order.status, order_id))

        if cur.rowcount == 0:
            raise LookupError(f"orders#{order_id}: рядка нема — його встигли видалити?")

        self._conn.execute("DELETE FROM order_lines WHERE order_id = ?", (order_id,))
        self._write_lines(order_id, order.lines)

    def delete(self, order):
        order_id = self._identified(order)
        self._conn.execute("DELETE FROM order_lines WHERE order_id = ?",  # явно, не каскадом
                           (order_id,))
        cur = self._conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        if cur.rowcount == 0:
            raise LookupError(f"orders#{order_id}: видаляти нема чого")

    # ── внутрішнє ──────────────────────────────────────────────────────────
    def _build(self, head, rows):
        if not rows:
            raise LookupError(
                f"orders#{head['id']}: голова є, позицій нема — база суперечить домену")
        lines = [OrderLine(r["sku"], r["qty"], Money(r["price_cents"], head["currency"]))
                 for r in rows]
        return Order(head["id"], datetime.fromisoformat(head["placed_at"]),
                     lines, head["status"])

    def _write_lines(self, order_id, lines):
        self._conn.executemany(
            "INSERT INTO order_lines (order_id, position, sku, qty, price_cents) "
            "VALUES (?, ?, ?, ?, ?)",
            [(order_id, i, l.sku, l.qty, l.price.cents) for i, l in enumerate(lines)])

    @staticmethod
    def _identified(order):
        if order.id is None:
            raise ValueError("об'єкт без id: спершу insert")
        return order.id
