def decode_item(it):
    """MISSION_ITEM_INT → людські величини. Цілі 1e-7° → градуси."""
    return dict(
        seq=it.seq,
        command=it.command,
        lat=it.x * 1e-7,          # ЦІЛЕ 1e-7 градуса → градуси
        lon=it.y * 1e-7,
        alt=it.z,                 # метри — але в ЯКІЙ системі? каже it.frame
        frame=it.frame)

def verify_mission(items, expected, tol_m=0.5):
    """Звірити зчитану місію з еталоном. expected — список тих самих кортежів wp().
       Друкує таблицю; повертає True, якщо все збіглося в межах допуску."""
    # Пастка №3 у зародку: звіряти можна ЛИШЕ повний список.
    if items is None or len(items) != len(expected):
        got = 0 if items is None else len(items)
        print(f"звірка НЕМОЖЛИВА: зчитано {got}, а задумано {len(expected)} — "
              f"список неповний, будь-яка звірка тут бреше")
        return False

    print(f"{'#':>2}  {'команда':<16} {'lat':>12} {'lon':>12} "
          f"{'alt':>7} {'frame':>6}  результат")
    ok_all = True
    # 1 градус широти ≈ 111 111 м; для довготи множимо на cos(широти).
    import math
    DEG_M = 111_111.0
    for it, exp in zip(items, expected):
        d = decode_item(it)
        # горизонтальна відстань між зчитаним і задуманим, у метрах
        dlat_m = (d['lat'] - exp['x'] * 1e-7) * DEG_M
        dlon_m = (d['lon'] - exp['y'] * 1e-7) * DEG_M * math.cos(math.radians(d['lat']))
        dist_m = math.hypot(dlat_m, dlon_m)

        bad = []
        if d['command'] != exp['command']:      bad.append("команда")
        if d['frame']   != exp['frame']:        bad.append("frame(висота!)")
        if dist_m       > tol_m:                bad.append(f"зсув {dist_m:.2f}м")
        if abs(d['alt'] - exp['z']) > tol_m:    bad.append("висота")

        mark = "OK" if not bad else "✗ " + ", ".join(bad)
        if bad: ok_all = False
        print(f"{d['seq']:>2}  {d['command']:<16} {d['lat']:>12.7f} {d['lon']:>12.7f} "
              f"{d['alt']:>7.1f} {d['frame']:>6}  {mark}")
    return ok_all
