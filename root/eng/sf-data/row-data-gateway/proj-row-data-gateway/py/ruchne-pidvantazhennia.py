from collections import defaultdict

class OrderLineFinder:
    @staticmethod
    def find_by_orders(order_ids):
        marks = ",".join("?" * len(order_ids))         # → WHERE order_id IN (?, ?, …)
        rows = db.execute(
            f"SELECT * FROM order_lines WHERE order_id IN ({marks})", order_ids
        ).fetchall()
        return [OrderLineGateway._load(r) for r in rows]

orders = OrderFinder.find_by_status("paid")            # 1 запит
lines = OrderLineFinder.find_by_orders([o.id for o in orders])   # +1 на ВСІХ
by_order = defaultdict(list)
for ln in lines:
    by_order[ln.order_id].append(ln)                   # групуємо в пам'яті
for o in orders:
    o.lines = by_order[o.id]
