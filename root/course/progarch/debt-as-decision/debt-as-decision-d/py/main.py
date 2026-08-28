from typing import Protocol

# Шов: контракт, який бачить решта коду.
class EnergyRollup(Protocol):
    def kwh_for_day(self, home: str, day: str) -> float: ...

# Свідомий борг: наївний підсумок сирих рядків на кожен запит.
# Розплата за масштабом реальна — але ОБМЕЖЕНА цим одним класом.
class NaiveRollup:
    def __init__(self, db):
        self.db = db

    def kwh_for_day(self, home: str, day: str) -> float:
        rows = self.db.query(
            "SELECT power_w FROM telemetry WHERE home=%s AND day=%s", (home, day))
        return sum(r.power_w / 1000 / 3600 for r in rows)  # груба інтеграція

# Панель бачить лише шов — не знає про наївність під ним.
def render_panel(rollup: EnergyRollup, home: str) -> None:
    today = rollup.kwh_for_day(home, "2026-07-11")
    # ...малюємо число
