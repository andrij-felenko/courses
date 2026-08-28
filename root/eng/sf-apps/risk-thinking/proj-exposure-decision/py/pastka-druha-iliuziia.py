# Прогнати варіант у двох крайнощах: оптимістичній (усі p × 0.6)
# і песимістичній (усі p × 1.4, але не вище 1.0). Дає ВИЛКУ експозиції.
def exposure_range(v: Variant) -> tuple[float, float]:
    lo = hi = 0.0
    for r in v.risks:
        p_lo = r.p * 0.6
        p_hi = min(r.p * 1.4, 1.0)   # ймовірність не буває > 1
        lo += p_lo * r.loss
        hi += p_hi * r.loss
    return lo, hi

# Чи стійкий вирок? Вирок надійний ЛИШЕ якщо вилки не перекриваються:
# найгірший випадок переможця все одно кращий за найкращий випадок суперника.
def verdict_robust(a: Variant, b: Variant) -> None:
    a_lo, a_hi = exposure_range(a)
    b_lo, b_hi = exposure_range(b)
    print(f"{a.name}: {a_lo:.1f} .. {a_hi:.1f}")
    print(f"{b.name}: {b_lo:.1f} .. {b_hi:.1f}")
    if a_hi < b_lo:
        print(f"Вирок СТІЙКИЙ: {a.name} кращий навіть у найгіршому для себе разі.")
    elif b_hi < a_lo:
        print(f"Вирок СТІЙКИЙ: {b.name} кращий навіть у найгіршому для себе разі.")
    else:
        print("Вирок ХИТКИЙ: вилки перекриваються — цифри не вирішують, "
              "потрібні інші аргументи або точніші оцінки.")
