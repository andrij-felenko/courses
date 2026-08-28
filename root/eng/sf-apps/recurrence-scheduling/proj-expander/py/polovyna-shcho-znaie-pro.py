"""Друга половина: локалізація й головний цикл."""
from datetime import timezone
from zoneinfo import ZoneInfo


def to_instant(local: datetime, tz: ZoneInfo, disambiguate: str = "compatible") -> datetime | None:
    """Перетворює настінний час у зоновану мить UTC.
    Підтримує режими обробки часових аномалій (весняна прогалина, осінній дубль)."""
    aware = local.replace(tzinfo=tz)
    # Перевірка обертанням: чи існує такий настінний час без спотворення
    roundtrip = aware.astimezone(timezone.utc).astimezone(tz).replace(tzinfo=None)
    if roundtrip == local:
        return aware.astimezone(timezone.utc)

    # Якщо час потрапив у весняну прогалину (DST Spring Forward)
    if disambiguate == "compatible" or disambiguate == "forward":
        # Зсуваємо вперед на 1 годину до найближчого дійсного часу
        shifted = local + timedelta(hours=1)
        shifted_aware = shifted.replace(tzinfo=tz)
        if shifted_aware.astimezone(timezone.utc).astimezone(tz).replace(tzinfo=None) == shifted:
            return shifted_aware.astimezone(timezone.utc)
    elif disambiguate == "reject":
        return None

    return None


def expand(rule: Rule, start_local: datetime, tzid: str, after: datetime,
           limit: int, horizon_years: int = 10, disambiguate: str = "compatible") -> list[datetime]:
    """Головний генератор наступних спрацювань із фільтрацією винятків та DST."""
    tz = ZoneInfo(tzid)
    start_utc = to_instant(start_local, tz, disambiguate)
    if start_utc is None:
        start_utc = start_local.replace(tzinfo=timezone.utc)

    horizon = date(after.year + horizon_years, 12, 31)   # запобіжник від вічного циклу
    out: list[datetime] = []
    seen, i = 0, 0

    while len(out) < limit:
        first, marks = candidates(rule, start_local, i)
        if first > horizon:
            break
        i += 1
        for local in marks:
            inst = to_instant(local, tz, disambiguate)
            if inst is None or inst < start_utc:
                continue                                 # неіснуючі або попередні не беремо

            # Фільтрація дат винятків EXDATE
            if inst in rule.exdates:
                continue

            seen += 1
            if rule.count is not None and seen > rule.count:
                return out
            if rule.until is not None and inst > rule.until:
                return out
            if inst > after:                             # строго після — не включно
                out.append(inst)
                if len(out) == limit:
                    return out
    return out


def demo_suite():
    """Тестова валідація типових сценаріїв розгортача."""
    # 1. Щомісяця остання п'ятниця
    rule_last_fri = Rule(freq="MONTHLY", by_day=((-1, 4),), count=5)
    start = datetime(2026, 1, 1, 9, 0)
    res1 = expand(rule_last_fri, start, "Europe/Kyiv", after=start, limit=5)
    assert len(res1) == 5, "Має бути рівно 5 останніх п'ятниць"

    # 2. Зсув вихідних днів до понеділка з винятком EXDATE
    ex_date = datetime(2026, 3, 16, 7, 0, tzinfo=timezone.utc)
    rule_billing = Rule(freq="MONTHLY", by_monthday=(15,), shift_weekend="FORWARD", exdates={ex_date})
    res2 = expand(rule_billing, datetime(2026, 1, 15, 9, 0), "Europe/Kyiv", after=start, limit=4)
    assert ex_date not in res2, "Виняток EXDATE не повинен потрапити у видачу"

    # 3. Весняний стрибок через прогалину 03:30 (Київ, 29 березня 2026)
    rule_daily = Rule(freq="DAILY", count=5)
    res3 = expand(rule_daily, datetime(2026, 3, 27, 3, 30), "Europe/Kyiv", after=datetime(2026, 3, 27, 0, 0), limit=5)
    assert len(res3) == 5, "Має згенерувати 5 послідовних дійсних митей"
    return res1, res2, res3
