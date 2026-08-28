KR = 2                      # радіус ядра: 5 = 2*KR+1
W = (1, 4, 6, 4, 1)         # сума = 16 = 2^4


def clampi(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)


def blur_h(src, dst, w, h):
    """Горизонтальний прохід: src -> dst, кожен рядок згортається з W."""
    for y in range(h):
        row = y * w
        for x in range(w):
            acc = 0
            for t in range(-KR, KR + 1):
                xi = clampi(x + t, 0, w - 1)   # edge-clamp по краю рядка
                acc += W[t + KR] * src[row + xi]
            dst[row + x] = (acc + 8) >> 4      # /16 з округленням


def blur_v(src, dst, w, h):
    """Вертикальний прохід: src -> dst, кожен стовпець згортається з W."""
    for y in range(h):
        row = y * w
        for x in range(w):
            acc = 0
            for t in range(-KR, KR + 1):
                yi = clampi(y + t, 0, h - 1)   # edge-clamp по краю стовпця
                acc += W[t + KR] * src[yi * w + x]
            dst[row + x] = (acc + 8) >> 4


def gauss5_separable(src, dst, tmp, w, h):
    """Повне гаусове розмиття 5x5 двома проходами.
    tmp — проміжний буфер тих самих розмірів, що й кадр (виділяє викликач)."""
    blur_h(src, tmp, w, h)    # спершу рядки
    blur_v(tmp, dst, w, h)    # тоді стовпці
