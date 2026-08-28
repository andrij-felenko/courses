@dataclass(frozen=True)
class DailyRow:
    home_id: str
    day: str
    kwh: float
    # родовід:
    source_from: str          # межі вихідного вікна
    source_to: str
    pipeline_version: str     # яка версія конвеєра це порахувала
    schemas_seen: tuple       # СИРІ теги, як були на дроті — доказ для криміналістики

def daily_rows(raw, pre_meter, overrides, window, pipeline_version):
    """Незмінне вікно сирого → денні рядки з родоводом. Чиста функція."""
    homes = defaultdict(lambda: defaultdict(list))     # дім → пристрій → рядки
    seen = defaultdict(set)                             # (дім, день) → сирі теги schema
    for r in raw:
        homes[r.home_id][r.device_id].append(r)
        seen[(r.home_id, day_of(r.ts))].add(r.schema)  # ← сирий тег, не виправлений
    agg = defaultdict(float)                            # (дім, день) → Вт·год
    for home, devices in homes.items():
        for dev, rows in devices.items():
            for day, wh in device_day_wh(rows, pre_meter.get(dev), overrides).items():
                agg[(home, day)] += wh
    frm, to = day_of(window[0]), day_of(window[1])
    return [
        DailyRow(home, day, round(wh / 1000, 1),        # Вт·год → кВт·год, 1 знак
                 frm, to, pipeline_version, tuple(sorted(seen[(home, day)])))
        for (home, day), wh in sorted(agg.items())
    ]
