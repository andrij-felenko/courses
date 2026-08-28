def solve(a, b, c):
    if a == 0 and b == 0:                        # ліва частина завжди 0
        return ("all", None) if c == 0 else ("none", None)
    g, x0, y0 = ext_gcd(a, b)
    if g < 0:                                    # НСД тримаємо додатним
        g, x0, y0 = -g, -x0, -y0
    if c % g != 0:                               # критерій: d мусить ділити c
        return ("none", None)
    k = c // g
    x1, y1 = x0 * k, y0 * k                       # один розв'язок (може бути величезний)
    sx, sy = b // g, -(a // g)                    # крок родини (b/d, −a/d)
    if sx != 0:                                   # звести перший розв'язок до найменшого |x|
        m = abs(sx); t = (x1 % m - x1) // sx
    else:                                         # b = 0: x зафіксований, зводимо y
        m = abs(sy); t = (y1 % m - y1) // sy
    return ("family", (x1 + sx * t, y1 + sy * t, sx, sy, g))
