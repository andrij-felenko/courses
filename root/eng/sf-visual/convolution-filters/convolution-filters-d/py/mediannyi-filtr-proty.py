def clampi(x, lo, hi):
    return lo if x < lo else (hi if x > hi else x)

# медіана дев'яти: відсортувати достатньо, щоб 5-й елемент став на місце
def median9(v):
    # частковий вибірковий прохід: після i=4 v[4] = 5-й за порядком
    for i in range(5):
        for j in range(i + 1, 9):
            if v[i] > v[j]:
                v[i], v[j] = v[j], v[i]
    return v[4]

def median3(src, dst, w, h):
    for y in range(h):
        for x in range(w):
            v = []                                    # зібрати окіл 3x3
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    yi = clampi(y + dy, 0, h - 1)
                    xi = clampi(x + dx, 0, w - 1)
                    v.append(src[yi*w + xi])
            dst[y*w + x] = median9(v)
