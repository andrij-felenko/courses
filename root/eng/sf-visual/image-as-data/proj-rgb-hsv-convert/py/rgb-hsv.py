# RGB888 -> HSV, кожен канал 0..255. Тон закодовано як 0..255 (увесь круг у байт).
# Без float. int(a / b) відтворює C-ділення з обрізанням до нуля (a буває від'ємним).
def rgb_to_hsv_u8(r, g, b):
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    delta = cmax - cmin

    v = cmax                                    # V = Cmax

    if cmax == 0:
        return 0, 0, 0                          # чорне: S,H не визначені
    s = (delta * 255) // cmax                   # S = Δ/Cmax, масштаб ×255

    if delta == 0:
        return 0, s, v                          # сіре: тон не визначений

    # тон рахуємо у проміжній шкалі 0..1530 (6 секторів по 255), тоді /6 у 0..255
    if cmax == r:
        hue = 0    + int(255 * (g - b) / delta)  # червоний сектор
    elif cmax == g:
        hue = 510  + int(255 * (b - r) / delta)  # зелений  (+2·255)
    else:
        hue = 1020 + int(255 * (r - g) / delta)  # синій    (+4·255)

    if hue < 0:
        hue += 1530                             # загорнути від'ємний бік (≡ mod 6)
    h = hue // 6                                # 1530 → 255
    return h, s, v
