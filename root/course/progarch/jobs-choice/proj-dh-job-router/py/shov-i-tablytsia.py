# ── ОДИН ШОВ + таблиця маршрутів (ЄДИНЕ місце, де клас зустрічає субстрат) ──
def make_system():
    db = Db()
    broker = Broker()
    db_queue = DbQueue(db)
    outbox = OutboxBridge(db, broker)

    route = {
        "cacheWarm":    MemoryQueue(),  # втратне — хай гине на рестарті
        "transcode":    db_queue,       # народжене із записом кліпа → атомарно в тій же транзакції
        "notify":       db_queue,       # теж із бізнес-запису → дефолт
        "report":       db_queue,       # cron кладе сюди ж (без tx — свій)
        "fleetRollout": outbox,         # корінець у базі атомарно, relay розсіює в брокер
        "telemetry":    broker,         # потік із пристроїв — не для гарячої таблиці jobs
    }

    def enqueue(job: Job, tx: Tx | None = None) -> None:
        route[job.cls].put(job, tx)     # виклику байдуже, який субстрат унизу

    return SimpleNamespace(db=db, broker=broker, outbox=outbox, route=route, enqueue=enqueue)
