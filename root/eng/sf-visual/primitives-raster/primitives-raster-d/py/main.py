# Заливка многокутника по рядках. poly — список вершин (x, y) за обходом.
def fill_polygon(fb, W, H, poly, color):
    N = len(poly)
    # межі по Y — лише рядки, які фігура справді накриває
    ymin = max(0,     min(p[1] for p in poly))
    ymax = min(H - 1, max(p[1] for p in poly))

    for y in range(ymin, ymax + 1):
        xs = []
        # зібрати x-перетини ребер із серединою рядка (y + 0.5)
        for i in range(N):
            (xi, yi), (xj, yj) = poly[i], poly[i - 1]   # i-1 замикає на останню вершину
            # ребро перетинає рядок, якщо y між його кінцями (півінтервал!)
            if (yi <= y < yj) or (yj <= y < yi):
                # лінійна інтерполяція x у точці перетину
                xs.append(xi + (y - yi) * (xj - xi) // (yj - yi))
        xs.sort()                                       # перетини зліва направо
        # залити спани між парами 0-1, 2-3, ...
        for a in range(0, len(xs) - 1, 2):
            hspan(fb, W, H, xs[a], xs[a + 1], y, color)
