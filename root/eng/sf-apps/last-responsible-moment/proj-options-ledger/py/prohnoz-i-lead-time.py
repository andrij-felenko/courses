Window = dict[str, list[float]]   # signal → [найдавніший … найновіший]

def latest(xs: list[float]) -> float:
    return xs[-1]

def slope_per_week(xs: list[float]) -> float:
    """Нахил (одиниць за тиждень) методом найменших квадратів по вікну."""
    n = len(xs)
    if n < 2:
        return 0.0
    mean_x = (n - 1) / 2                    # тижні 0…n-1
    mean_y = sum(xs) / n
    num = sum((i - mean_x) * (x - mean_y) for i, x in enumerate(xs))
    den = sum((i - mean_x) ** 2 for i in range(n))
    return num / den if den else 0.0

def project(xs: list[float], lead_weeks: float) -> float:
    """Прогноз на L тижнів наперед — лінійна екстраполяція краю вікна."""
    return latest(xs) + slope_per_week(xs) * lead_weeks

def past(v: float, thr: float, direction: str) -> bool:
    return v >= thr if direction == "rising" else v <= thr

# Зводимося на ФАКТІ (arm по latest), стріляємо за ПРОГНОЗОМ (fire по project).
def is_armed(t: Trigger, w: Window) -> bool:
    hits = []
    for c in t.conditions:
        xs = w.get(c.signal)
        hits.append(past(latest(xs), c.arm_at, c.direction) if xs else False)
    return all(hits) if t.mode == "all" else any(hits)

def is_firing(t: Trigger, w: Window) -> bool:
    hits = []
    for c in t.conditions:
        xs = w.get(c.signal)
        hits.append(past(project(xs, t.lead_weeks), c.fire_at, c.direction) if xs else False)
    return all(hits) if t.mode == "all" else any(hits)
