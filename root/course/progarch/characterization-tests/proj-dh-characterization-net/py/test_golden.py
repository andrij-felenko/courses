# test_golden.py
from pathlib import Path
import random
from datetime import datetime
import pytest
import scheduler
from conftest import FrozenClock

DAY = [
    ("холодний ранок, дім прокидається", 7,
     {"hall": {"temp": 15.2, "motion": True, "lux": 8}, "bed": {"temp": 16.0}},
     {"threshold": 20.0, "night": True, "morning": 21.0}),
    ("робочий день, нікого вдома", 14,
     {"hall": {"temp": 20.5}, "bed": {"temp": 23.0}}, {"threshold": 20.0}),
    ("спекотний полудень", 13,
     {"hall": {"temp": 26.0, "motion": True, "lux": 300}}, {"threshold": 20.0}),
    ("відпустка, прохолодний ранок", 7,
     {"hall": {"temp": 15.0}, "bed": {"temp": 14.0}},
     {"threshold": 20.0, "vacation": True, "morning": 21.0}),
    ("ніч, давач вітальні мовчить", 2,
     {"hall": {"temp": float("nan")}, "bed": {"temp": 17.0}},
     {"threshold": 20.0, "night": True}),
    ("відпустка, мороз", 3,
     {"hall": {"temp": 8.0}}, {"threshold": 20.0, "vacation": True}),
]


def render_day(monkeypatch):
    lines = []
    for label, hour, sensors, rules in DAY:
        monkeypatch.setattr(scheduler, "datetime", FrozenClock(datetime(2026, 1, 15, hour, 0)))
        monkeypatch.setattr(scheduler, "random", random.Random(0))   # зерно на кожен сценарій
        lines.append(f"=== {label} ({hour:02d}:00) ===")
        lines += scheduler.plan(sensors, rules)
    return "\n".join(lines)


def test_day_matches_golden(monkeypatch):
    got = render_day(monkeypatch)
    approved = Path(__file__).parent / "golden" / "day.approved.txt"
    if not approved.exists():                       # перший прогін — нема з чим звіряти
        approved.with_suffix(".received.txt").write_text(got, encoding="utf-8")
        pytest.fail("нема еталона: переглянь day.received.txt і, якщо ок, перейменуй у .approved")
    assert got == approved.read_text(encoding="utf-8")
