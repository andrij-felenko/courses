def signed_area(x, y):
    """Орієнтована площа замкненого сліду: ½·Σ(xᵢ·yᵢ₊₁ − xᵢ₊₁·yᵢ)."""
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def phase_shift(x, y):
    """Зсув фаз каналу x відносно y, радіани. Форма дає модуль, обхід — знак."""
    x = x - x.mean()
    y = y - y.mean()
    c = float(x @ y) / math.sqrt(float(x @ x) * float(y @ y))
    return math.copysign(math.acos(max(-1.0, min(1.0, c))), signed_area(x, y))
