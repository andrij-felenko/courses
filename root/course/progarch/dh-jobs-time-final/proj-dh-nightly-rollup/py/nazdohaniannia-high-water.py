def due_days(zone_name: str, last_done: date) -> list[date]:
    """Локальні доби, ще НЕ згорнуті: (last_done, сьогодні), обидва кінці виключно."""
    today = datetime.now(ZoneInfo(zone_name)).date()
    days, cur = [], last_done + timedelta(days=1)          # перша НЕзгорнута
    while cur < today:                                     # строго ДО «сьогодні»
        days.append(cur)
        cur += timedelta(days=1)                           # чиста дата — DST тут не живе
    return days

def apply_policy(days: list[date], p: str) -> list[date]:
    if len(days) <= 1 or p == "catchup":
        return days                                        # усі по черзі
    if p == "skip":
        return days[-1:]                                   # лише найсвіжіша, решта — дірки
    return days                                            # coalesce: усі → в ОДНЕ вікно
