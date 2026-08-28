import numpy as np

# 1) еталон: вертикальні смужки періоду `period` пікселів (жорсткий тест на муар)
def make_reference(H, W, period):
    x = np.arange(W)
    v = np.where((x // period) & 1, 230, 30).astype(np.uint8)   # чорно-білі смуги
    row = np.repeat(v[:, None], 3, axis=1)                       # сіра сцена: R=G=B!
    return np.broadcast_to(row, (H, W, 3)).copy()

# 2) мозаїка RGGB: у кожній точці лишаємо лише «свій» канал
def mosaic_rggb(ref):
    H, W, _ = ref.shape
    raw = np.empty((H, W), dtype=np.uint8)
    yy, xx = np.indices((H, W))
    ey, ex = yy & 1, xx & 1
    raw[(ey == 0) & (ex == 0)] = ref[..., 0][(ey == 0) & (ex == 0)]  # червоний піксель
    raw[(ey == 1) & (ex == 1)] = ref[..., 2][(ey == 1) & (ex == 1)]  # синій
    green = (ey != ex)
    raw[green] = ref[..., 1][green]                                   # зелений
    return raw

# 3) PSNR між демозаїченим і еталоном (усі три канали разом)
def psnr(a, b):
    diff = a.astype(np.float64) - b.astype(np.float64)
    mse = np.mean(diff * diff)                    # усі три канали разом
    if mse <= 0.0:
        return 99.0                               # ідеальний збіг
    return 10.0 * np.log10(255.0 * 255.0 / mse)

# зведення докупи
def evaluate(method, period, H=64, W=64):
    ref = make_reference(H, W, period)
    raw = mosaic_rggb(ref)
    out = method(raw)
    return psnr(out, ref)
