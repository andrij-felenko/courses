class ScheduleV:
    def __init__(self, time: str, zone: str):
        self.time, self.zone = time, zone      # ДЖЕРЕЛО ПРАВДИ: намір
        self.next_fire_utc: datetime | None = None   # КЕШ: похідна мить для індексу

    def resolve(self, after: datetime) -> None:
        # перекувати кеш із наміру за ЧИННИМИ правилами (той самий next_fire_B)
        self.next_fire_utc = next_fire_B(after, {"time": self.time, "zone": self.zone})

    def due(self, now: datetime) -> bool:
        # планувальник питає дешево, за готовою міттю — як у способі А
        return self.next_fire_utc is not None and self.next_fire_utc <= now

# ПІСЛЯ ОНОВЛЕННЯ tzdata — перекувати ВСІ ще не запущені розклади:
def on_tzdata_update(schedules: list[ScheduleV], now: datetime) -> None:
    for s in schedules:
        s.resolve(now)                          # ← без цього рядка В тихо стає А
