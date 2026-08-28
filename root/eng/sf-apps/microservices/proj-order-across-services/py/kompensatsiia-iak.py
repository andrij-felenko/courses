# Компенсація на боці СКЛАДУ: повертаємо раніше списаний товар.
class StockConsumer:
    # ... on_order_placed як вище ...

    async def on_order_cancelled(self, evt: OrderCancelledEvent) -> None:
        async with self._db.transaction() as tx:
            # та сама дедуплікація — компенсація теж має бути безпечною до повтору
            fresh = await tx.try_insert("processed_events", {
                "event_id": evt.event_id, "handled_at": datetime.now(timezone.utc),
            })
            if not fresh:
                return

            # КОМПЕНСАЦІЯ: дописуємо товар назад — логічний антипод списання
            for item in evt.payload.items:
                await tx.execute(
                    "UPDATE stock SET qty = qty + :q WHERE sku = :s",
                    {"q": item.qty, "s": item.sku},
                )
