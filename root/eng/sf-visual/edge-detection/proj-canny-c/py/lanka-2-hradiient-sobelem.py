# Собелеві ядра.  Gx — вертикальні межі, Gy — горизонтальні.
SOBEL_X = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.int32)
SOBEL_Y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.int32)

def sobel_grad(img):
    """Повертає (mag: int32, dir: uint8 0..3).
    Сектор — вісь градієнта (впоперек межі), уздовж неї й порівнює NMS.
    0 = ліво/право (межа вертикальна);           2 = верх/низ (межа горизонтальна);
    1 = ~45°: градієнт на діагоналі \\ (межа /);  3 = ~135°: градієнт на діагоналі / (межа \\)."""
    H, W = img.shape
    mag = np.zeros((H, W), dtype=np.int32)
    dir = np.zeros((H, W), dtype=np.uint8)
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            win = img[y - 1:y + 2, x - 1:x + 2].astype(np.int32)
            gx = int((SOBEL_X * win).sum())
            gy = int((SOBEL_Y * win).sum())
            # сила: округлене евклідове; для МК можна abs(gx)+abs(gy)
            mag[y, x] = int(np.hypot(gx, gy) + 0.5)

            # напрям → один із 4 секторів (кут за модулем 180°)
            ang = np.degrees(np.arctan2(gy, gx))  # -180..180
            if ang < 0:
                ang += 180.0                       # 0..180
            if ang < 22.5 or ang >= 157.5:
                s = 0   # ~0°   → сусіди ліво/право
            elif ang < 67.5:
                s = 1   # ~45°  → сусіди по діагоналі \ (↖↘)
            elif ang < 112.5:
                s = 2   # ~90°  → сусіди верх/низ
            else:
                s = 3   # ~135° → сусіди по діагоналі / (↙↗)
            dir[y, x] = s
    return mag, dir
