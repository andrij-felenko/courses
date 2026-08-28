# Беквіл однієї партиції: читаємо старе пачками за курсором (краще з РЕПЛІКИ,
# щоб не душити головний вузол), ідемпотентно пишемо в нове, чекпойнт рухаємо
# ПІСЛЯ запису. Повтор пачки безпечний: upsert за (device_id, ts) перезаписує комірку.
def backfill_partition(part, checkpoint, batch=10_000):
    last_key = checkpoint.load(part.id)                 # де спинилися минулого разу
    while True:
        rows = old_replica.read_batch(part, after=last_key, limit=batch, ts_lt=T0)
        if not rows:
            break
        new.upsert_many(rows)                           # ідемпотентно за первинним ключем
        last_key = rows[-1].key                         # (device_id, ts) останнього рядка
        checkpoint.save(part.id, last_key)              # рухаємо чекпойнт лише ТЕПЕР
    checkpoint.mark_done(part.id)
