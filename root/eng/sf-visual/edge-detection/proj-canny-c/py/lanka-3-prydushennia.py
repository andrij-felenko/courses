def nms_quantized(mag, dir):
    """За квантованим сектором лишаємо тільки локальні максимуми вздовж градієнта."""
    H, W = mag.shape
    out = np.zeros((H, W), dtype=np.int32)   # край лишиться 0
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            m = mag[y, x]
            s = dir[y, x]                    # два сусіди вздовж градієнта
            if s == 0:
                a, b = mag[y, x - 1], mag[y, x + 1]          # ліво / право
            elif s == 1:
                a, b = mag[y - 1, x - 1], mag[y + 1, x + 1]  # діаг. \ : ↖ / ↘
            elif s == 2:
                a, b = mag[y - 1, x], mag[y + 1, x]          # верх / низ
            else:
                a, b = mag[y + 1, x - 1], mag[y - 1, x + 1]  # діаг. / : ↙ / ↗
            if m >= a and m >= b:
                out[y, x] = m                # гребінь — лишаємо силу
    return out
