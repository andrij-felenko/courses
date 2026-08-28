from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone

UTC = timezone.utc
STEP_SEC = 3600      # номінальний крок відліку (тест — погодинний; насправді секунди)

def day_of(ts: int) -> str:
    return datetime.fromtimestamp(ts, UTC).date().isoformat()   # "2026-06-10"

@dataclass(frozen=True)
class Raw:
    home_id: str
    device_id: str
    ts: int           # epoch, секунди
    schema: int       # 1 → value є Вт (потужність); 2 → value є Вт·год (лічильник)
    value: int        # на дроті: `w` для schema:1, `wh` для schema:2 — тут одне число

@dataclass(frozen=True)
class Override:
    device_id: str
    ts_from: int
    ts_to: int
    schema: int       # чим форма БУЛА насправді

def eff_schema(r: Raw, overrides) -> int:
    for o in overrides:
        if o.device_id == r.device_id and o.ts_from <= r.ts < o.ts_to:
            return o.schema        # виправлення живе тут, а не в сирому рядку
    return r.schema

def device_day_wh(rows, pre_meter, overrides) -> dict:
    """Один пристрій, усі його відліки за вікно → {день: Вт·год}. Чиста функція."""
    rows = sorted(rows, key=lambda r: r.ts)
    out = defaultdict(float)
    meter = pre_meter                      # показ лічильника ДО вікна (для schema:2)
    for i, r in enumerate(rows):
        day = day_of(r.ts)
        if eff_schema(r, overrides) == 2:                  # лічильник: різниця показів
            if meter is not None:
                out[day] += r.value - meter
            meter = r.value
        else:                                              # потужність: інтеграл по dt
            nxt = rows[i + 1].ts if i + 1 < len(rows) else r.ts + STEP_SEC
            out[day] += r.value * (nxt - r.ts) / 3600.0
    return dict(out)
