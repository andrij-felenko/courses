import math
import random


def line_through(p, q, min_base):
    """Пряма a·x + b·y + c = 0 крізь дві точки, нормована: a² + b² = 1.
    Повертає None, якщо вибірка вироджена (точки надто близько)."""
    a = q[1] - p[1]                       # Δy
    b = p[0] - q[0]                       # −Δx
    n = math.hypot(a, b)                  # = відстань між p і q, тобто база вибірки
    if n < min_base:
        return None                       # ділити на це не можна — та й не варто
    a, b = a / n, b / n
    return a, b, -(a * p[0] + b * p[1])


def count_inliers(model, pts, t):
    """Скільки точок лежать до моделі ближче за поріг t."""
    a, b, c = model
    return sum(1 for x, y in pts if abs(a * x + b * y + c) <= t)


def collect_inliers(model, pts, t):
    a, b, c = model
    return [(x, y) for x, y in pts if abs(a * x + b * y + c) <= t]


def refine(pts):
    """Тотальні найменші квадрати: пряма крізь центроїд уздовж головної осі хмари.
    Мінімізує суму квадратів ПЕРПЕНДИКУЛЯРНИХ відхилень — ту саму міру, якою
    міряла згода. Вертикальних прямих не боїться."""
    m = len(pts)
    xm = sum(x for x, _ in pts) / m
    ym = sum(y for _, y in pts) / m
    sxx = sum((x - xm) ** 2 for x, _ in pts)
    syy = sum((y - ym) ** 2 for _, y in pts)
    sxy = sum((x - xm) * (y - ym) for x, y in pts)
    th = 0.5 * math.atan2(2 * sxy, sxx - syy)   # напрямок головної осі
    a, b = -math.sin(th), math.cos(th)          # нормаль до неї — вже одинична
    return a, b, -(a * xm + b * ym)


def ransac_line(pts, t, k, min_base, rng):
    """Повертає (уточнена модель, згодні точки) або (None, [])."""
    m = len(pts)
    if m < 2:
        return None, []
    best, best_count = None, 0
    for _ in range(k):
        i = rng.randrange(m)                    # 1. мінімальна вибірка — 2 точки
        j = rng.randrange(m - 1)
        if j >= i:
            j += 1                              # рівномірно серед усіх, крім i
        model = line_through(pts[i], pts[j], min_base)   # 2. модель по вибірці
        if model is None:
            continue                            # вироджена вибірка — спроба намарне
        cnt = count_inliers(model, pts, t)      # 3. згода: у циклі тільки лічимо
        if cnt > best_count:                    # 4. новий рекорд
            best, best_count = model, cnt
    if best is None:
        return None, []
    inliers = collect_inliers(best, pts, t)     # список — один раз, для переможця
    return refine(inliers), inliers             # уточнення ТІЛЬКИ по згодних
