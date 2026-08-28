def report(s: FpvSystem, speed_kmh: float) -> None:
    g = glass_to_glass(s)
    period = frame_period_ms(s.fps)
    load = compute_load_ms(s)
    fits = fits_frame_deadline(s)
    margin = reaction_margin_ms(g)

    print(f"== {s.name} ({s.fps} к/с) ==")
    if g.lo == g.hi:
        print(f"  Скло-скло:     {g.lo:.1f} мс (стала)")
    else:
        print(f"  Скло-скло:     {g.lo:.1f}-{g.hi:.1f} мс (змінна)")

    print(f"  Наосліп @{speed_kmh:.0f} км/год: "
          f"{blind_distance_m(g.lo, speed_kmh):.2f}-"
          f"{blind_distance_m(g.hi, speed_kmh):.2f} м")

    fits_str = "ВЛАЗИТЬ" if fits else "НЕ ВЛАЗИТЬ"
    print(f"  Кадровий період: {period:.2f} мс, обробка: {load:.1f} мс -> {fits_str}")

    margin_note = "" if margin > 0 else "(!) з'їдено весь бюджет"
    print(f"  Запас реакції:   {margin:.0f} мс {margin_note}\n")
