# -*- coding: utf-8 -*-
"""Розгортання рекурентного правила: календарна половина."""
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, time
from calendar import monthrange


@dataclass(frozen=True)
class Rule:
    freq: str                         # DAILY | WEEKLY | MONTHLY | YEARLY
    interval: int = 1
    by_month: tuple = ()              # 1..12
    by_monthday: tuple = ()           # 1..31 і -1..-31 (рахує з кінця місяця)
    by_day: tuple = ()                # ((номер|None, день тижня), …); «-1FR» → (-1, 4)
    by_setpos: tuple = ()             # відбір у межах ОДНОГО періоду
    count: int | None = None
    until: datetime | None = None     # мить в UTC, включно
    exdates: set = field(default_factory=set)  # множина дат-винятків (EXDATE)
    workday_only: bool = False        # вимагати лише робочі дні (пн-пт)
    shift_weekend: str = "NONE"       # "NONE" | "FORWARD" (до пн) | "BACKWARD" (до пт)


def period_dates(rule: Rule, start: datetime, i: int) -> list[date]:
    """Дати i-го періоду. i рахується від періоду ПОЧАТКУ, а не від
    останнього спрацювання — саме це тримає крок INTERVAL на місці."""
    k = i * rule.interval
    if rule.freq == "DAILY":
        return [start.date() + timedelta(days=k)]
    if rule.freq == "WEEKLY":
        first = start.date() - timedelta(days=start.weekday()) + timedelta(weeks=k)
        return [first + timedelta(days=j) for j in range(7)]
    if rule.freq == "MONTHLY":
        y, m = divmod(start.year * 12 + start.month - 1 + k, 12)
        return _month_dates(y, m + 1)
    if rule.freq == "YEARLY":
        # звужуємо ще на породженні: перебирати 366 дат, щоб лишити 28, — марно
        months = rule.by_month or tuple(range(1, 13))
        return [d for m in sorted(months) for d in _month_dates(start.year + k, m)]
    raise ValueError("невідома частота: " + rule.freq)


def _month_dates(y: int, m: int) -> list[date]:
    return [date(y, m, j) for j in range(1, monthrange(y, m)[1] + 1)]


def matches(rule: Rule, d: date, dates: list[date]) -> bool:
    """Чи справджують уточнення саме цю дату. dates — увесь період:
    без нього не порахувати «остання п'ятниця»."""
    if rule.by_month and d.month not in rule.by_month:
        return False
    if rule.by_monthday:
        last = monthrange(d.year, d.month)[1]
        if not any(d.day == (v if v > 0 else last + 1 + v) for v in rule.by_monthday):
            return False
    if rule.by_day:
        same = [x for x in dates if x.weekday() == d.weekday()]
        for ordinal, wd in rule.by_day:
            if wd != d.weekday():
                continue
            if ordinal is None:
                return True
            pos = same.index(d) + 1 if ordinal > 0 else same.index(d) - len(same)
            if pos == ordinal:
                return True
        return False
    return True


def apply_weekend_shift(d: date, mode: str) -> date:
    """Зсув дати, якщо вона припадає на суботу або неділю."""
    wd = d.weekday()
    if wd == 5:  # Субота
        if mode == "FORWARD":
            return d + timedelta(days=2)  # Понеділок
        if mode == "BACKWARD":
            return d - timedelta(days=1)  # П'ятниця
    elif wd == 6:  # Неділя
        if mode == "FORWARD":
            return d + timedelta(days=1)  # Понеділок
        if mode == "BACKWARD":
            return d - timedelta(days=2)  # П'ятниця
    return d


def candidates(rule: Rule, start: datetime, i: int) -> tuple[date, list[datetime]]:
    """Упорядкований набір настінних міток i-го періоду після всіх уточнень."""
    dates = period_dates(rule, start, i)
    kept = [d for d in dates if matches(rule, d, dates)]
    if rule.by_setpos:                       # відбір бачить УВЕСЬ набір періоду
        n = len(kept)
        idx = sorted({(p - 1 if p > 0 else n + p) for p in rule.by_setpos})
        kept = [kept[j] for j in idx if 0 <= j < n]
    
    # Застосування бізнес-правил вихідних днів
    if rule.shift_weekend != "NONE":
        kept = [apply_weekend_shift(d, rule.shift_weekend) for d in kept]
    elif rule.workday_only:
        kept = [d for d in kept if d.weekday() < 5]

    tod = start.time()
    return dates[0], [datetime.combine(d, tod) for d in kept]
