from math import gcd

def crt_pair(a1, n1, a2, n2):
    """Звести x ≡ a1 (mod n1) та x ≡ a2 (mod n2) в одне рівняння.
    Повертає (a, НСК) або None, якщо система суперечлива."""
    g = gcd(n1, n2)
    if (a2 - a1) % g:
        return None                                  # умова сумісності не виконана
    lcm = n1 // g * n2                               # ділимо ДО множення — щоб не роздути
    t = (a2 - a1) // g * pow(n1 // g, -1, n2 // g) % (n2 // g)
    return (a1 + n1 * t) % lcm, lcm

def crt(residues, moduli):
    """Склеїти всю систему драбинкою: пара за парою."""
    a, n = 0, 1                                      # x ≡ 0 (mod 1) — істинне для всіх x
    for ai, ni in zip(residues, moduli):
        merged = crt_pair(a, n, ai % ni, ni)
        if merged is None:
            return None
        a, n = merged
    return a, n

print(crt([2, 3, 2], [3, 5, 7]))      # (23, 105)  — задача Сунь-цзи
print(crt_pair(3, 4, 5, 6))           # (11, 12)   — модулі НЕ взаємно прості, та це не завада
print(crt_pair(0, 4, 1, 6))           # None       — парне й непарне водночас
