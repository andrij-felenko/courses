import numpy as np

# Адаптивний поріг ADAPTIVE_THRESH_MEAN_C через інтегральне зображення.
# Повертає маску: 1, де піксель ТЕМНІШИЙ за (локальне середнє − C) — «чорнило» мітки.
# win — сторона вікна (непарна), у OpenCV-aruco її беруть у діапазоні 3..23.
def adaptive_threshold(img, win, C):
    H, W = img.shape
    # 1) Інтегральне зображення з нульовими рядком і стовпцем (padding).
    integ = np.zeros((H + 1, W + 1), dtype=np.int64)
    integ[1:, 1:] = np.cumsum(np.cumsum(img.astype(np.int64), axis=0), axis=1)

    r = win // 2
    out = np.zeros((H, W), dtype=np.uint8)
    for y in range(H):
        y0, y1 = max(0, y - r), min(H - 1, y + r)
        for x in range(W):
            x0, x1 = max(0, x - r), min(W - 1, x + r)
            area = (x1 - x0 + 1) * (y1 - y0 + 1)
            # сума по прямокутнику [x0..x1]×[y0..y1] — чотири кути таблиці:
            s = (integ[y1 + 1, x1 + 1] - integ[y0, x1 + 1]
                 - integ[y1 + 1, x0] + integ[y0, x0])
            mean = int(s // area)
            out[y, x] = 1 if int(img[y, x]) < mean - C else 0   # темніше → «чорнило»
    return out
