from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

COLS = "id, customer_id, total_cents, status, updated_at"


class OrderTableGateway:
    def __init__(self, db):                        # з'єднання приходить ЗЗОВНІ
        self.db = db

    def find(self, order_id):
        with self.db.cursor(row_factory=dict_row) as cur:
            cur.execute(f"SELECT {COLS} FROM orders WHERE id = %s", (order_id,))
            return cur.fetchone()                  # немає рядка — None, не виняток

    def find_by_status(self, status, limit=500):
        with self.db.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"SELECT {COLS} FROM orders WHERE status = %s ORDER BY id LIMIT %s",
                (status, limit),
            )
            return cur.fetchall()

    def insert(self, customer_id, total_cents, status):
        with self.db.cursor() as cur:
            cur.execute(
                "INSERT INTO orders (customer_id, total_cents, status) "
                "VALUES (%s, %s, %s) RETURNING id",
                (customer_id, total_cents, status),
            )
            return cur.fetchone()[0]               # ключ віддає база, не код

    def update_status(self, order_id, status):
        with self.db.cursor() as cur:
            cur.execute(
                "UPDATE orders SET status = %s, updated_at = now() WHERE id = %s",
                (status, order_id),
            )
            return cur.rowcount                    # 0 = такого рядка не було

    def remove(self, order_id):
        with self.db.cursor() as cur:
            cur.execute("DELETE FROM orders WHERE id = %s", (order_id,))
            return cur.rowcount


pool = ConnectionPool(CONNINFO)

# Межа транзакції: вихід із блоку — COMMIT, виняток усередині — ROLLBACK.
with pool.connection() as conn:
    gw = OrderTableGateway(conn)                   # те саме conn на всі виклики
    for row in gw.find_by_status("paid"):
        if row["total_cents"] > 100_000:           # правило живе ЗОВНІ шлюзу
            gw.update_status(row["id"], "review")
