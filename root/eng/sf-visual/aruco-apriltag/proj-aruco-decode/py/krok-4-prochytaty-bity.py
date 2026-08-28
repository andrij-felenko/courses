GRID = 6                                # мітка 6×6 (рамка + 4×4 даних)
CANON = 48                              # S: 8 пікселів на клітинку (GRID*8) — з запасом
IGN = 0.13                              # відступ від краю клітинки (як у OpenCV)

# Прочитати сітку GRID×GRID: cells[gy][gx] — середня яскравість серединки клітинки.
def read_grid(img, Hi):
    cell = CANON / GRID
    m = cell * IGN                                  # поле, яке ігноруємо
    cells = [[0] * GRID for _ in range(GRID)]
    for gy in range(GRID):
        for gx in range(GRID):
            x0, x1 = gx * cell + m, (gx + 1) * cell - m
            y0, y1 = gy * cell + m, (gy + 1) * cell - m
            total = cnt = 0
            Yc = y0 + 0.5
            while Yc < y1:
                Xc = x0 + 0.5
                while Xc < x1:
                    v = sample_canonical(img, Hi, Xc, Yc)
                    if v >= 0:
                        total += v
                        cnt += 1
                    Xc += 1.0
                Yc += 1.0
            cells[gy][gx] = total // cnt if cnt else 0
    return cells

# Перетворити яскравості клітинок на біти (1 = біле) спільним порогом.
# Поріг — середина між найтемнішою й найсвітлішою клітинками (стійко до світла).
def cells_to_bits(cells):
    flat = [v for row in cells for v in row]
    thr = (min(flat) + max(flat)) // 2
    return [[1 if cells[gy][gx] > thr else 0       # світліше за поріг → біле
             for gx in range(GRID)] for gy in range(GRID)]
