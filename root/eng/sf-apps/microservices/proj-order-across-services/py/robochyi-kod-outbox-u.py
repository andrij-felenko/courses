from dataclasses import dataclass
import json, uuid
from datetime import datetime, timezone

@dataclass
class PlaceOrder:
    customer_id: str
    items: list[LineItem]

class OrderService:
    def __init__(self, db: Db) -> None:
        self._db = db   # приватна база сервісу замовлень

    async def place_order(self, cmd: PlaceOrder) -> str:
        order = Order.create(cmd.customer_id, cmd.items)

        # ── ОДНА локальна транзакція: замовлення + намір сповістити склад ──
        async with self._db.transaction() as tx:
            await tx.insert("orders", {
                "id": order.id,
                "customer_id": order.customer_id,
                "status": "placed",
                "total": order.total,
            })

            # рядок OUTBOX — намір, що поїде в чергу окремим реле.
            # event_id генеруємо ТУТ і кладемо в тіло — саме за ним споживач
            # упізнаватиме дублі. topic каже реле, у яку чергу це слати.
            await tx.insert("outbox", {
                "event_id": str(uuid.uuid4()),
                "topic": "OrderPlaced",
                "payload": json.dumps({"order_id": order.id, "items": order.items}),
                "sent": False,
                "created_at": datetime.now(timezone.utc),
            })
        # ← коміт: або лягли ОБИДВА рядки, або жоден. Подвійного запису немає.

        return order.id
