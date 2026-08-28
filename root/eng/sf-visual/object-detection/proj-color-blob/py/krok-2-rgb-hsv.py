def rgb_to_hsv(r, g, b):                    # h2 = тон/2 (0..179), як у OpenCV
    mx, mn = max(r, g, b), min(r, g, b)
    d = mx - mn                                          # хрома
    v = mx                                               # яскравість = max
    s = 255 * d // mx if mx else 0                       # насиченість
    if d == 0:
        return (0, s, v)                                 # сірий: тон не визначений

    if mx == r:     h = 60 * (g - b) // d                # сектор навколо червоного
    elif mx == g:   h = 120 + 60 * (b - r) // d          # навколо зеленого
    else:           h = 240 + 60 * (r - g) // d          # навколо синього
    if h < 0:
        h += 360
    return (h // 2, s, v)                                # ділимо на 2, щоб влізло в 0..179
