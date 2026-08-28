KR = 2                       # радіус: 5 = 2*KR+1
W = (1, 4, 6, 4, 1)          # сума 16 = 2^4

def clampi(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)

# горизонтальний прохід: кожен рядок згортаємо з W
def blur_h(s, d, w, h):
    for y in range(h):
        for x in range(w):
            a = 0
            for t in range(-KR, KR + 1):
                a += W[t + KR] * s[y*w + clampi(x + t, 0, w - 1)]
            d[y*w + x] = (a + 8) >> 4            # /16 з округленням

# вертикальний прохід: кожен стовпець згортаємо з тим самим W
def blur_v(s, d, w, h):
    for y in range(h):
        for x in range(w):
            a = 0
            for t in range(-KR, KR + 1):
                a += W[t + KR] * s[clampi(y + t, 0, h - 1)*w + x]
            d[y*w + x] = (a + 8) >> 4

def gauss5(src, dst, tmp, w, h):
    blur_h(src, tmp, w, h)   # спершу рядки
    blur_v(tmp, dst, w, h)   # тоді стовпці
