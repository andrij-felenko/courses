# RGB888 -> HSV, усе в 0..255. H закодовано як 0..255 (а не 0..360°).
def _trunc_div(a, b):
    return int(a / b)   # ділення з відкиданням до нуля, як у C

def rgb_to_hsv_u8(r, g, b):
    cmax = max(r, g, b)   # max каналу
    cmin = min(r, g, b)   # min каналу
    delta = cmax - cmin

    v = cmax                          # V = Cmax

    if cmax == 0:
        return 0, 0, v                # чорне: S,H не визначені → 0
    s = (delta * 255) // cmax         # S = Δ/Cmax, масштаб ×255

    if delta == 0:
        return 0, s, v                # сіре: тон не визначений → 0

    # рахуємо тон у 0..1530 (6 секторів по 255), тоді стиснемо до 0..255
    if cmax == r:
        hue = 0    + _trunc_div(255 * (g - b), delta)   # червоний сектор
    elif cmax == g:
        hue = 510  + _trunc_div(255 * (b - r), delta)   # зелений  (+2·255)
    else:
        hue = 1020 + _trunc_div(255 * (r - g), delta)   # синій    (+4·255)

    if hue < 0:
        hue += 1530                   # загорнути від'ємний бік (як mod 6)
    h = hue // 6                      # 0..1530 → 0..255
    return h, s, v
