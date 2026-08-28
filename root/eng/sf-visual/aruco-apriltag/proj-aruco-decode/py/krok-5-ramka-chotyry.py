from dataclasses import dataclass

# Порахувати 16-бітний код із матриці внутрішніх 4×4 бітів (рядок за рядком).
def bits4x4_to_code(bit):
    code = 0
    for gy in range(1, 5):                          # внутрішні клітинки 1..4
        for gx in range(1, 5):
            code = (code << 1) | (bit[gy][gx] & 1)
    return code

# Повернути матрицю 4×4 бітів на 90° за годинниковою: dst[x][3-y] = src[y][x].
def rot90_4x4(src):
    dst = [[0] * 4 for _ in range(4)]
    for y in range(4):
        for x in range(4):
            dst[x][3 - y] = src[y][x]
    return dst

def hamming16(a, b):
    return bin(a ^ b).count("1")                    # XOR, тоді порахувати одиниці

# Словник: коди у ЖОРСТКОМУ порядку рамка-чорна, лише внутрішні 4×4.
# (реальний ArUco зберігає всі 4 оберти заздалегідь; ми обертаємо матрицю на льоту)
@dataclass
class Dict:
    code: list[int]
    max_correct: int

# Звірити прочитані біти зі словником по 4 обертах.
# Повертає (id, rot), де rot — на скільки *90° мітка повернута (0..3),
# щоб викликач упорядкував кути; або (-1, 0), якщо мітку не впізнано.
def identify(bit, dct):
    m = [[bit[y + 1][x + 1] for x in range(4)] for y in range(4)]   # внутрішні 4×4

    best_id, best_dist, best_rot = -1, 0x7fffffff, 0
    for k in range(4):                              # чотири оберти
        # зібрати код поточного оберту
        code = 0
        for y in range(4):
            for x in range(4):
                code = (code << 1) | (m[y][x] & 1)
        # мінімальний Гемінг до всіх слів словника
        for i, word in enumerate(dct.code):
            d = hamming16(code, word)
            if d < best_dist:
                best_dist, best_id, best_rot = d, i, k
        m = rot90_4x4(m)                            # повернути на наступні 90°

    if best_dist <= dct.max_correct:                # у межах виправлення → впізнано
        return best_id, best_rot
    return -1, 0                                     # задалеко від усіх → чуже
