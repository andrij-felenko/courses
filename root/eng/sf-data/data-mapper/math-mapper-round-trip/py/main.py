def check_laws(save, load, objects, rows,
               eq=lambda a, b: a == b, row_eq=lambda a, b: a == b):
    """Закон 1 — рівність. Закон 2 — НЕ рівність, а лише нерухомість другого прогону."""
    e = lambda r: save(load(r))

    # Обов'язок: нічого не загубити.
    for o in objects:
        if not eq(load(save(o)), o):
            raise AssertionError(f"закон 1 впав на {o!r}: об'єкт повернувся іншим")

    # Наслідок: e(r) може НЕ дорівнювати r — але e(e(r)) мусить дорівнювати e(r).
    for r in rows:
        once = e(r)
        twice = e(once)
        if not row_eq(twice, once):
            raise AssertionError(f"закон 2 впав на {r!r}: друге збереження щось змінило")

    return "обидва закони тримаються"


# колонка-текст placed_at ↔ datetime
save = lambda d: d.isoformat()
load = lambda s: datetime.fromisoformat(s)

check_laws(save, load,
           objects=[datetime(2026, 7, 14), datetime(2026, 7, 14, 9, 31, 7, 250000)],
           rows=["2026-07-14", "2026-07-14 00:00:00", "2026-07-14T00:00:00"])
