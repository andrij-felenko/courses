async def write_reading(self, r: Reading) -> None:
    # Старе — джерело правди: якщо воно не прийняло рядок, це справжня
    # помилка, і вона летить користувачу.
    await self.old.insert(r)
    try:
        await self.new.upsert(r)          # нове — «як вийде»
    except Exception as e:
        self.divergence.inc()             # лічильник розбіжності — стежимо БЕЗПЕРЕРВНО
        log.warning("new-store write failed: device=%s ts=%s err=%s",
                    r.device_id, r.ts, e)
        # навмисно ковтаємо: нове ще не джерело правди, прогалину залатає звірка
