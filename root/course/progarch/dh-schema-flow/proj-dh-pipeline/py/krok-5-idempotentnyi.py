class MemStore:
    def __init__(self, rows): self.rows = rows
    def raw_between(self, a, b): return [r for r in self.rows if a <= r.ts < b]
    def last_meter_before(self, a):
        out = {}
        for r in sorted(self.rows, key=lambda r: r.ts):
            if r.ts < a and r.schema == 2:
                out[r.device_id] = r.value       # останній до вікна перемагає
        return out

class MemWarehouse:
    def __init__(self): self.daily = {}
    def upsert_daily(self, rows):
        for r in rows:
            self.daily[(r.home_id, r.day)] = r   # ЗАМІНА за ключем → ідемпотентно

def midnight(y, m, d): return int(datetime(y, m, d, tzinfo=UTC).timestamp())

def test_schema2_counts_right():
    t0 = midnight(2026, 6, 10)
    rows = [Raw("h", "d-bad", t0, 2, 145203), Raw("h", "d-bad", t0 + 3600, 2, 145210)]
    assert device_day_wh(rows, None, [])["2026-06-10"] == 7        # різниця показів

def test_mistag_overestimates():
    t0 = midnight(2026, 6, 10)                                     # ті самі числа,
    rows = [Raw("h", "d-bad", t0, 1, 145203), Raw("h", "d-bad", t0 + 3600, 1, 145210)]
    wh = device_day_wh(rows, None, [])["2026-06-10"]              # але тег БРЕШЕ
    assert wh == 145203 + 145210                                  # = 290413 Вт·год
    assert wh > 1000 * 7                                          # завищення на порядки

def test_override_heals():
    t0 = midnight(2026, 6, 10)
    rows = [Raw("h", "d-bad", t0, 1, 145203), Raw("h", "d-bad", t0 + 3600, 1, 145210)]
    fix = [Override("d-bad", t0, t0 + 86400, 2)]                  # «це насправді лічильник»
    assert device_day_wh(rows, None, fix)["2026-06-10"] == 7      # вилікувано, сире ціле

def test_reprocess_is_idempotent():
    t0 = midnight(2026, 6, 10)
    store = MemStore([
        Raw("h1", "d-fridge", t0 - 3600, 2, 145000),             # carry-in ДО вікна
        Raw("h1", "d-fridge", t0 + 6 * 3600, 2, 145300),
        Raw("h1", "d-fridge", t0 + 12 * 3600, 2, 145700),
        Raw("h1", "d-fridge", t0 + 18 * 3600, 2, 146200),
    ])
    window = (t0, t0 + 86400)
    a = MemWarehouse(); run_etl(store, a, window, "etl-2026.06")
    b = MemWarehouse(); run_etl(store, b, window, "etl-2026.06")
    run_etl(store, b, window, "etl-2026.06")                      # ще раз поверх
    assert a.daily == b.daily                                    # 1×, 2×, 3× — той самий стан
    row = a.daily[("h1", "2026-06-10")]
    assert row.kwh == 1.2                                        # 146200 − 145000 = 1200 Вт·год
    assert row.schemas_seen == (2,)                              # родовід: лише форма 2
