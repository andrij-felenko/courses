import math

Point = tuple[float, float]        # (x, y) у метрах


def net_displacement(pts: list[Point]) -> tuple[Point, float]:
    """Вектор rₙ − r₀ та його модуль. Порожньо/один відлік → нуль."""
    if len(pts) < 2:
        return (0.0, 0.0), 0.0
    (x0, y0), (xn, yn) = pts[0], pts[-1]
    dx, dy = xn - x0, yn - y0
    return (dx, dy), math.hypot(dx, dy)


def path_length(pts: list[Point]) -> float:
    """Сума довжин відрізків між сусідніми відліками."""
    total = 0.0
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        total += math.hypot(xb - xa, yb - ya)
    return total
