def clampi(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)

# один піксель гаусу 3x3; сума ваг 16 → нормування = зсув на 4 з округленням
def gauss3_px(s, w, h, x, y):
    wk = ((1, 2, 1), (2, 4, 2), (1, 2, 1))
    acc = 0
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            yi = clampi(y + dy, 0, h - 1)
            xi = clampi(x + dx, 0, w - 1)
            acc += wk[dy+1][dx+1] * s[yi*w + xi]
    return (acc + 8) >> 4                 # +8 = пів-дільника → округлення до найближчого
