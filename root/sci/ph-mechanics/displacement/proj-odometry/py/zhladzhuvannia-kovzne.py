def moving_average(pts: list[Point], w: int) -> list[Point]:
    """Згладити відліки вікном ±w (проста ковзна середня по обох осях)."""
    n = len(pts)
    out: list[Point] = []
    for i in range(n):
        lo, hi = max(0, i - w), min(n, i + w + 1)
        seg = pts[lo:hi]
        xs = sum(p[0] for p in seg) / len(seg)
        ys = sum(p[1] for p in seg) / len(seg)
        out.append((xs, ys))
    return out


# ужиток: спершу згладити, тоді звичайний шлях
s = path_length(moving_average(pts, w=2))
