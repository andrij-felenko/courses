# thin ← локальні максимуми сили вздовж квантованого напряму.
def nms_quantized(H, W, mag, dir):
    thin = [[0] * W for _ in range(H)]
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            c = mag[y][x]
            s = dir[y][x]                              # сектор 0..3
            if s == 0:                                 # ─
                a, b = mag[y][x - 1],     mag[y][x + 1]
            elif s == 1:                               # /
                a, b = mag[y + 1][x - 1], mag[y - 1][x + 1]
            elif s == 2:                               # │
                a, b = mag[y - 1][x],     mag[y + 1][x]
            else:                                      # \
                a, b = mag[y - 1][x - 1], mag[y + 1][x + 1]
            if c >= a and c >= b:
                thin[y][x] = c                         # на гребені — лишаємо
    return thin
