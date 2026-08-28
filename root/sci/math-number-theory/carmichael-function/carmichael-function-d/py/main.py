from math import gcd

def lcm(a: int, b: int) -> int:
    return a // gcd(a, b) * b

def carmichael_lambda(n: int) -> int:
    """λ(n) = НСК по простих степенях p^k у розкладі n; для 2^k при k≥3 — 2^(k-2)."""
    result, m, p = 1, n, 2
    while p * p <= m:
        if m % p == 0:
            k = 0
            while m % p == 0:              # витягуємо весь степінь p^k
                m //= p
                k += 1
            if p == 2 and k >= 3:
                lam = 1 << (k - 2)         # аномалія: 2^(k-2), а не 2^(k-1)
            elif p == 2 and k == 2:
                lam = 2
            elif p == 2:
                lam = 1
            else:
                lam = (p - 1) * p**(k - 1)  # непарне просте: φ(p^k)
            result = lcm(result, lam)
        p += 1
    if m > 1:                             # лишився один великий простий дільник p^1
        result = lcm(result, m - 1)
    return result

assert carmichael_lambda(8)   == 2
assert carmichael_lambda(360) == 12
assert carmichael_lambda(561) == 80       # знадобиться нижче
assert carmichael_lambda(7)   == 6        # для простого збігається з p − 1
