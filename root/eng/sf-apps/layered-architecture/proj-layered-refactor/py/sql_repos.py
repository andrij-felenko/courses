# infra/sql_repos.py — тут (і лише тут) живе SQL
from domain.order import Order
from domain.repos import ProductRepo, OrderRepo

class SqlProductRepo:                 # структурно задовольняє ProductRepo
    def __init__(self, conn):
        self.conn = conn
    def find(self, sku: str):
        row = self.conn.execute(
            "SELECT price, stock FROM products WHERE sku = ?", (sku,)).fetchone()
        return (row[0], row[1]) if row else None

class SqlOrderRepo:                    # структурно задовольняє OrderRepo
    def __init__(self, conn):
        self.conn = conn
    def add(self, order: Order) -> int:
        return self.conn.execute(
            "INSERT INTO orders(total) VALUES (?)",
            (order.total(),)).lastrowid
    def reduce_stock(self, sku: str, qty: int) -> None:
        self.conn.execute(
            "UPDATE products SET stock = stock - ? WHERE sku = ?", (qty, sku))
