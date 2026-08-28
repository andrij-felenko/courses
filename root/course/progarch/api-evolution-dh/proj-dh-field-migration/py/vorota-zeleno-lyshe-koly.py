import time
from collections import defaultdict
from dataclasses import dataclass

DAY_MS = 86_400_000

class WindowedReadCounter:
    def __init__(self) -> None:
        # (поле, когорта) → {epoch-день: лічильник}
        self._buckets: dict[tuple[str, str], dict[int, int]] = defaultdict(
            lambda: defaultdict(int))

    @staticmethod
    def _day(ts_ms: float) -> int:
        return int(ts_ms // DAY_MS)

    def hit(self, field: str, cohort: str) -> None:
        self._buckets[(field, cohort)][self._day(time.time() * 1000)] += 1

    def per_cohort(self, field: str, window_ms: int) -> dict[str, int]:
        since = self._day(time.time() * 1000 - window_ms)
        out: dict[str, int] = defaultdict(int)
        for (f, cohort), days in self._buckets.items():
            if f != field:
                continue
            n = sum(c for d, c in days.items() if d >= since)
            if n > 0:                      # у вікні читали → когорта в грі
                out[cohort] = n
        return dict(out)


@dataclass
class GateResult:
    field: str
    green: bool
    window_days: float
    still_reading: dict[str, int]


def can_contract(field: str, counter: WindowedReadCounter, window_ms: int) -> GateResult:
    per_cohort = counter.per_cohort(field, window_ms)   # когорти — із телеметрії!
    return GateResult(
        field=field,
        window_days=window_ms / DAY_MS,
        green=len(per_cohort) == 0,        # зелено ⟺ НУЛЬ у КОЖНІЙ когорті
        still_reading=per_cohort,
    )
