class StockConsumer:
    def __init__(self, db: Db) -> None:
        self._db = db   # приватна база сервісу складу

    # Викликається чергою на кожну доставлену подію OrderPlaced.
    async def on_order_placed(self, evt: OrderPlacedEvent) -> None:
        async with self._db.transaction() as tx:
            # 1) ДЕДУП: пробуємо застовпити event_id. Первинний ключ на
            #    processed_events робить повторну вставку неможливою — другий
            #    прохід тієї самої події тут спіткнеться, і ми просто вийдемо.
            fresh = await tx.try_insert("processed_events", {
                "event_id": evt.event_id,
                "handled_at": datetime.now(timezone.utc),
            })
            if not fresh:
                return   # вже бачили цей event_id — дубль, тихо виходимо

            # 2) ДІЯ: списуємо товар. У ТІЙ САМІЙ транзакції, що й відмітка
            #    дедупу, тож «оброблено» і «списано» або разом, або ніяк.
            for item in evt.payload.items:
                await tx.execute(
                    "UPDATE stock SET qty = qty - :q WHERE sku = :s AND qty >= :q",
                    {"q": item.qty, "s": item.sku},
                )
        # ← коміт: дедуп і списання нероздільні
