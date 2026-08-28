# infra/pg_orders.py ── ЄДИНЕ місце, що знає SQL. Мапить домен ↔ рядок.
import json
from typing import Optional
from domain.order import Order, Line


class PgOrders:
    def __init__(self, pool):
        self._pool = pool

    async def save(self, o: Order) -> None:
        await self._pool.execute(
            """insert into orders(id, email, lines, total) values ($1, $2, $3, $4)
               on conflict (id) do update set lines = excluded.lines, total = excluded.total""",
            o.id, o.email, json.dumps([l.__dict__ for l in o.lines]), o.total(),
        )

    async def by_id(self, id: str) -> Optional[Order]:
        row = await self._pool.fetchrow("select email, lines from orders where id = $1", id)
        if row is None:
            return None
        lines = [Line(**l) for l in json.loads(row["lines"])]
        return Order.place(id, row["email"], lines)
