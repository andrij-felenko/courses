# warped — розпрямлене зображення мітки, масив W×W (numpy), 8 біт/піксель.
# GRID=6 (з рамкою); внутрішні 4×4 несуть дані. Повертаємо 16-бітний сирий код.
GRID = 6

# Середня яскравість клітинки (gx,gy) — беремо серединку клітинки, без країв.
def cell_mean(warped, W, gx, gy):
    cell = W // GRID                    # скільки пікселів припадає на одну клітинку
    x0 = gx * cell + cell // 4          # відступ від краю клітинки, щоб не чіпати
    y0 = gy * cell + cell // 4          # сусідню (краї «пливуть» після розпрямлення)
    x1 = gx * cell + 3 * cell // 4
    y1 = gy * cell + 3 * cell // 4
    return int(warped[y0:y1, x0:x1].mean())   # 0..255

# Перевірити рамку й прочитати внутрішні 4×4 у 16-бітний код (чорне=0, біле=1).
def read_marker(warped, W):
    THR = 128                          # поріг чорне/біле (спрощено; краще адаптивний)
    # 1) Рамка: усе зовнішнє кільце має бути ЧОРНЕ, інакше це не мітка.
    for g in range(GRID):
        if (cell_mean(warped, W, g, 0)        > THR or   # верхній край
            cell_mean(warped, W, g, GRID - 1) > THR or   # нижній край
            cell_mean(warped, W, 0, g)        > THR or   # лівий край
            cell_mean(warped, W, GRID - 1, g) > THR):    # правий край
            return None                # рамка пробита — відкинути кандидата
    # 2) Внутрішні 4×4 → біти коду.
    code = 0
    for gy in range(1, 5):
        for gx in range(1, 5):
            code <<= 1
            if cell_mean(warped, W, gx, gy) > THR:       # біла = 1
                code |= 1
    return code                        # код прочитано; далі — звірка зі словником
