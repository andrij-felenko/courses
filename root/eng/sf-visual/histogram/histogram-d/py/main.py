import numpy as np

def build_lut(hist, n):
    lut = np.empty(256, dtype=np.uint8)
    if n == 0:                                 # порожній кадр — ділити нема на що
        return np.arange(256, dtype=np.uint8)  # тотожна таблиця
    acc = 0                                    # накопичена сума = CDF·n
    for v in range(256):
        acc += int(hist[v])                    # acc = h(0)+…+h(v)
        # round( (acc/n)·255 ) = (acc·255 + n/2) // n   — цілочисельно
        mapped = (acc * 255 + n // 2) // n
        lut[v] = mapped                        # 0…255 гарантовано (acc ≤ n)
    return lut
