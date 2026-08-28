# Один шов постановки: enqueue() ховає, на якому субстраті ляже задача.
# Вирішує таблиця маршрутів за КЛАСОМ роботи.
ROUTE = {
    "cache_warm":    memory,    # втратне — хай гине на рестарті
    "transcode":     db_queue,  # народжене із записом кліпа → атомарно в одній транзакції
    "notify":        db_queue,  # теж із бізнес-запису → дефолт
    "report":        db_queue,  # cron кладе сюди ж
    "fleet_rollout": broker,    # переріс базу: фан-аут на тисячі, throttle+DLQ з коробки
    "telemetry":     broker,    # потік із пристроїв — не для гарячої таблиці jobs
}

def enqueue(job):
    return ROUTE[job.cls].put(job)   # виклику байдуже, який субстрат унизу
