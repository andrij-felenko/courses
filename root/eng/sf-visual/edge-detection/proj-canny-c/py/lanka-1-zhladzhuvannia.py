import numpy as np

# Ціле ядро Гаусса 5×5 (σ≈1), сума ваг = 159.
GAUSS5 = np.array([
    [2,  4,  5,  4, 2],
    [4,  9, 12,  9, 4],
    [5, 12, 15, 12, 5],
    [4,  9, 12,  9, 4],
    [2,  4,  5,  4, 2],
], dtype=np.int32)

def gauss_blur(img):
    """Згладити img (H×W, uint8) → uint8. Край (рамку 2 пікселі) лишаємо як є."""
    H, W = img.shape
    out = img.copy()
    for y in range(2, H - 2):
        for x in range(2, W - 2):
            # до 255*159 = 40545 — int32 тримає без обгортання
            win = img[y - 2:y + 3, x - 2:x + 3].astype(np.int32)
            acc = int((GAUSS5 * win).sum())
            out[y, x] = acc // 159
    return out
