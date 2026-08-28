from datetime import datetime, date, time, timedelta, timezone
from zoneinfo import ZoneInfo          # жива база переведень IANA у stdlib

def local_midnight(d: date, zone: ZoneInfo) -> datetime:
    """Перша наявна мить локальної доби d — ручний аналог Temporal .startOfDay().
    Майже завжди це рівно 00:00; але зона, що колись переводила стрілки опівночі,
    могла НЕ мати 00:00 — тоді беремо мить, куди щілина його виштовхнула."""
    naive = datetime.combine(d, time(0, 0))
    dt = naive.replace(tzinfo=zone)                        # fold=0 → перша, якщо складка
    back = dt.astimezone(timezone.utc).astimezone(zone).replace(tzinfo=None)
    if back != naive:                                      # 00:00 у весняній щілині
        dt = back.replace(tzinfo=zone)                     # мить, куди щілина виштовхнула північ
    return dt

def local_day_window(zone_name: str, d: date) -> tuple[datetime, datetime, float]:
    zone = ZoneInfo(zone_name)
    start = local_midnight(d, zone)
    end   = local_midnight(d + timedelta(days=1), zone)    # наступна локальна північ
    hours = (end - start).total_seconds() / 3600           # 23 / 24 / 25 — саме собою
    return start.astimezone(timezone.utc), end.astimezone(timezone.utc), hours
