import math

def bilerp(mag, fy, fx):
    """Білінійна сила в (точно дробовій) точці (fy, fx) — змішування 4 сусідів."""
    H, W = mag.shape
    x0, y0 = math.floor(fx), math.floor(fy)
    if x0 < 0 or y0 < 0 or x0 + 1 >= W or y0 + 1 >= H:
        return 0.0
    tx, ty = fx - x0, fy - y0
    top = mag[y0,     x0] * (1 - tx) + mag[y0,     x0 + 1] * tx
    bot = mag[y0 + 1, x0] * (1 - tx) + mag[y0 + 1, x0 + 1] * tx
    return top * (1 - ty) + bot * ty

def nms_interp(mag, gx, gy):
    """NMS із білінійною інтерполяцією двох сусідів уздовж напряму градієнта."""
    H, W = mag.shape
    out = np.zeros((H, W), dtype=np.int32)
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            m = mag[y, x]
            if m == 0:
                continue
            n = math.hypot(gx[y, x], gy[y, x])
            if n < 1e-9:
                continue
            ux, uy = gx[y, x] / n, gy[y, x] / n   # одиничний градієнт
            f1 = bilerp(mag, y + uy, x + ux)       # вперед
            f2 = bilerp(mag, y - uy, x - ux)       # назад
            if m >= f1 and m >= f2:
                out[y, x] = m
    return out
