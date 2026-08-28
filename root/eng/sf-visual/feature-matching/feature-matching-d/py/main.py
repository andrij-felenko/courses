# відстань Гаммінга двох 256-бітних ORB-дескрипторів (8 слів по 32 біти)
def hamming256(a, b):
    dist = 0
    for x, y in zip(a, b):
        dist += (x ^ y).bit_count()  # XOR → лічба різних бітів
    return dist                      # 0 = однакові, 256 = усе навпаки

# для кожного дескриптора ліворуч знайти найближчий і другий праворуч,
# прийняти лише за пробою відношення (для Гаммінга — теж відношення відстаней)
def match_one(query, train, ratio):
    best, second, best_j = 1 << 30, 1 << 30, -1
    for j, t in enumerate(train):
        d = hamming256(query, t)
        if d < best:
            second, best, best_j = best, d, j
        elif d < second:
            second = d
    # збіг певний, лише коли найкращий помітно ближчий за другий
    if second > 0 and best < ratio * second:
        return best_j      # прийнято
    return -1              # неоднозначно — відкинути
