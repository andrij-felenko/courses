# -*- coding: utf-8 -*-
"""Межа: настінний час ↔ мить. Стандартна бібліотека, Python 3.9+."""
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc


def resolve_local(wall: datetime, zone: str) -> tuple[datetime, str]:
    """wall — НАЇВНИЙ настінний час (без tzinfo). Мить у UTC і вид збігу."""
    tz = ZoneInfo(zone)
    before = wall.replace(tzinfo=tz, fold=0)   # зсув, що діяв ДО переходу
    after = wall.replace(tzinfo=tz, fold=1)    # зсув, що діє ПІСЛЯ
    instant = before.astimezone(UTC)

    if before.utcoffset() == after.utcoffset():
        return instant, "exact"
    if instant.astimezone(tz).replace(tzinfo=None) != wall:
        return instant, "gap"          # напис не повернувся сам у себе
    return instant, "ambiguous"        # обидва прочитання дійсні, узяли перше


def format_in_zone(instant: datetime, zone: str) -> str:
    """Мить → напис у зоні читача: «2026-10-25 03:30 +0300»."""
    return instant.astimezone(ZoneInfo(zone)).strftime("%Y-%m-%d %H:%M %z")


def day_bounds(day: date, zone: str) -> tuple[datetime, datetime]:
    """Півзакритий проміжок [від, до) — доба користувача на осі митей."""
    lo, _ = resolve_local(datetime.combine(day, time(0, 0)), zone)
    hi, _ = resolve_local(datetime.combine(day + timedelta(days=1), time(0, 0)), zone)
    return lo, hi
