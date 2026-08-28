# Б: зберігаємо НАМІР — стінний час + назву зони. Мить рахуємо в останню секунду.
schedule = {"time": "07:00", "zone": "Europe/Kyiv"}

def next_fire_B(after: datetime, sched: dict) -> datetime:
    z = ZoneInfo(sched["zone"])
    hh, mm = map(int, sched["time"].split(":"))
    day = after.astimezone(z).date()
    while True:
        # 07:00 у зоні, зібране ЗА ЧИННИМ tzdata саме на цей день
        wall = datetime(day.year, day.month, day.day, hh, mm, tzinfo=z)
        fire = wall.astimezone(timezone.utc)
        if fire > after:
            return fire
        day += timedelta(days=1)
