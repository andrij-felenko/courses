import random

def is_probable_prime(n, k=20):
    if n < 4:
        return n in (2, 3)              # 2 і 3 прості; 0 та 1 — ні
    if n % 2 == 0:
        return False                    # усе парне, крім 2, складене
    for _ in range(k):
        a = random.randrange(2, n - 1)  # основа у діапазоні 2 … n−2
        if pow(a, n - 1, n) != 1:       # знайшовся свідок
            return False                # n НАПЕВНО складене
    return True                         # усі k основ промовчали → імовірно просте
