# adapters/pg.py ── ДРАЙВОВАНИЙ АДАПТЕР. Реалізує ЗамовленняСховище через Postgres.
import json
from order.core import ЗамовленняСховище, Замовлення, Позиція


class PgСховище(ЗамовленняСховище):
    def __init__(self, pool):
        self._pool = pool

    async def зберегти(self, з: Замовлення) -> None:
        await self._pool.execute(              # ← SQL живе ТІЛЬКИ в цьому файлі
            """INSERT INTO orders(id, email, positions, total)
               VALUES ($1, $2, $3, $4)""",
            з.id, з.пошта, json.dumps([п.__dict__ for п in з.позиції]), з.сума(),
        )

    async def узяти(self, id: str) -> Замовлення | None:
        рядок = await self._pool.fetchrow("SELECT * FROM orders WHERE id = $1", id)
        if рядок is None:
            return None
        позиції = [Позиція(**п) for п in json.loads(рядок["positions"])]
        return Замовлення.створити(рядок["id"], рядок["email"], позиції)
