from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

# А: рахуємо мить ЗАРАЗ, за сьогоднішнім зсувом, і морозимо її.
def freeze_utc(local: str, zone: str) -> datetime:
    z = ZoneInfo(zone)
    wall = datetime.fromisoformat(local).replace(tzinfo=z)  # 07:00 у Києві
    return wall.astimezone(timezone.utc)                    # → 05:00Z (бо взимку +02:00)

frozen = freeze_utc("2026-01-10T07:00", "Europe/Kyiv")      # 2026-01-10 05:00:00+00:00

# щоденне спрацювання: та сама година UTC, +24 години щодня
def next_fire_A(after: datetime) -> datetime:
    fire = frozen
    while fire <= after:
        fire += timedelta(days=1)   # ← 24 години — це ФІЗИКА, а не «завтра о 07:00»
    return fire
