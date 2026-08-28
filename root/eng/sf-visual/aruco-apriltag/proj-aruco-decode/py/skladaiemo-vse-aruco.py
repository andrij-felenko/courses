# Один кандидат quad (4 точки) → структура Marker (id=-1, якщо не мітка).
def decode_candidate(img, quad, dct):
    out = Marker()
    Hm = homography_to_square(quad, CANON)
    if Hm is None:                                  # вироджений кандидат
        return out
    Hi = invert3x3(Hm)
    if Hi is None:
        return out

    cells = read_grid(img, Hi)
    bit = cells_to_bits(cells)

    # рамка: рахуємо білі клітинки в зовнішньому кільці, поріг 35%
    border_white = border_total = 0
    for g in range(GRID):
        for gx, gy in ((g, 0), (g, GRID - 1), (0, g), (GRID - 1, g)):
            border_total += 1
            border_white += bit[gy][gx]
    if border_white * 100 > border_total * 35:      # рамка світла → не мітка
        return out

    id_, rot = identify(bit, dct)
    if id_ < 0:
        return out

    # упорядкувати кути під знайдений оберт: циклічний зсув на rot позицій
    out.id = id_
    for i in range(4):
        out.corner[i][0] = quad[(i + rot) & 3][0]
        out.corner[i][1] = quad[(i + rot) & 3][1]
    return out

# Головний вхід: кадр → список міток. find_quads дає крок контурів (крок 2).
def aruco_decode(img, dct):
    # Крок 1 — поріг у маску чорнила. Вікно 23, C=7 (типові для aruco).
    binmask = adaptive_threshold(img, 23, 7)

    # Крок 2 — контури по масці → чотирикутники-кандидати. (трасування опущено;
    #           find_quads повертає список quad-ів по масках)
    cands = find_quads(binmask)                     # заглушка інтерфейсу

    # Крок 3–5 — довести кожного кандидата до ID або відкинути.
    markers = []
    for quad in cands:
        m = decode_candidate(img, quad, dct)
        if m.id >= 0:
            markers.append(m)
    return markers
