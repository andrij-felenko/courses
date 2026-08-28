import numpy as np

NCLASS = 3   # напр. кіт / пес / птах

def mixup(a: np.ndarray, b: np.ndarray,
          ya: np.ndarray, yb: np.ndarray, lam: float):
    """Змішати два сірі кадри й ДВА ЇХНІ ЯРЛИКИ одним коефіцієнтом lam.
    a, b   — вхідні кадри w*h байтів (uint8, форма (h, w));
    ya, yb — вхідні ярлики (по NCLASS ймовірностей, сума = 1);
    повертає (out, yout) — змішаний кадр (uint8) і змішаний ярлик."""

    # 1) ПІКСЕЛІ: out = lam*a + (1-lam)*b, з округленням і в межах 0…255.
    # float() важливо: без нього lam*a порахується неточно (по uint8).
    v = lam * a.astype(np.float32) + (1.0 - lam) * b.astype(np.float32)
    # round — округлити до найближчого; clip — на випадок похибки float.
    out = np.clip(np.round(v), 0, 255).astype(np.uint8)

    # 2) ЯРЛИК: yout = lam*ya + (1-lam)*yb — ТА САМА формула, той самий lam.
    yout = lam * ya + (1.0 - lam) * yb

    return out, yout
