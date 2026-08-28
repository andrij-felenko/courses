def report(d: Design, mounts: int = 1) -> None:
    print(f"── Опора під {d.mass_kg:g} кг, трясіння {d.exc_hz:.1f} Гц, "
          f"ζ = {d.zeta:g}, ціль T = {d.target_T:g} ──")
    print(f"  власна частота  fₙ = {d.fn_hz:6.2f} Гц")
    print(f"  відношення      r  = {d.r_work:6.2f}   (робоча точка)")
    print(f"  статичний прогин δ = {d.defl_mm:6.2f} мм")
    print(f"  жорсткість      k  = {d.k_total/1000:6.1f} кН/м", end="")
    if mounts > 1:
        print(f"   ({d.k_total/1000/mounts:.1f} кН/м на кожну з {mounts})")
    else:
        print()
    print(f"  ізоляція на робочій частоті: {d.isolation_pct:.0f} %")

    # головна перевірка: чи ми справді в зоні ізоляції
    ok = d.r_work > R_THRESH
    mark = "OK" if ok else "!!"
    print(f"  [{mark}] r = {d.r_work:.2f} {'>' if ok else '<'} √2 = {R_THRESH:.2f}"
          f"  → {'зона ізоляції' if ok else 'ЗОНА ПІДСИЛЕННЯ — опора шкодить'}")

    # резонанс на пуску
    print(f"  [!!] на розгоні пройде резонанс: пік T ≈ {d.peak_T:.1f}× "
          f"коло {d.peak_rpm:.0f} об/хв (r ≈ {d.peak_r:.2f})")

    # надто м'яка опора
    if d.fn_hz < 2.5 or d.defl_mm > 25.0:
        print(f"  [!!] опора надто м'яка: прогин {d.defl_mm:.0f} мм / "
              f"fₙ {d.fn_hz:.1f} Гц — плаватиме й хитатиметься")
