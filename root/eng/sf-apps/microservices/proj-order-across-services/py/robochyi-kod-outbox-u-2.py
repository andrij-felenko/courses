class OutboxRelay:
    def __init__(self, db: Db, queue: Queue) -> None:
        self._db = db
        self._queue = queue

    # Викликається за розкладом (напр. кожні 200 мс) або петлею.
    async def flush(self) -> None:
        rows = await self._db.query(
            "SELECT * FROM outbox WHERE sent = false ORDER BY created_at LIMIT 100",
        )

        for row in rows:
            # Публікуємо ПЕРЕД тим, як позначити sent. Якщо впадемо між
            # publish і update — рядок лишиться sent=false, і наступний
            # прохід надішле його ЩЕ раз. Дубль на боці споживача безпечний
            # (він ідемпотентний), а от ВТРАТА події — ні. Тому саме такий порядок.
            await self._queue.publish(row["topic"], {
                "event_id": row["event_id"],   # той самий ключ дедуплікації
                "payload": json.loads(row["payload"]),
            })
            await self._db.execute(
                "UPDATE outbox SET sent = true WHERE event_id = ?", [row["event_id"]],
            )
