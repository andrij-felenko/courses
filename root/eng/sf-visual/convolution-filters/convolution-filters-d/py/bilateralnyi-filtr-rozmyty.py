import math

R = 2                         # радіус вікна: 5x5

# білатеральний фільтр одного каналу uint8; ss — просторова сигма, sr — яскравісна
def bilateral(src, dst, w, h, ss, sr):
    gs = [[0.0] * (2*R+1) for _ in range(2*R+1)]   # просторові ваги наперед
    for dy in range(-R, R + 1):
        for dx in range(-R, R + 1):
            gs[dy+R][dx+R] = math.exp(-(dx*dx + dy*dy) / (2.0*ss*ss))
    for y in range(h):
        for x in range(w):
            wsum = 0.0
            acc = 0.0
            c = src[y*w + x]                       # яскравість центру
            for dy in range(-R, R + 1):
                for dx in range(-R, R + 1):
                    yi, xi = y + dy, x + dx
                    if yi < 0 or yi >= h or xi < 0 or xi >= w:
                        continue
                    p = src[yi*w + xi]
                    d = p - c                                 # різниця яскравості
                    gr = math.exp(-(d*d) / (2.0*sr*sr))       # яскравісна вага
                    ww = gs[dy+R][dx+R] * gr                  # добуток двох ваг
                    acc += ww * p
                    wsum += ww
            dst[y*w + x] = int(acc / wsum + 0.5)
