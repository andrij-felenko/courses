from math import gcd

def factorize(n):
    """Розклад n на прості: список пар (p, k) для кожного p^k."""
    factors, p = [], 2
    while p * p <= n:
        if n % p == 0:
            k = 0
            while n % p == 0:
                n //= p; k += 1
            factors.append((p, k))
        p += 1
    if n > 1:                       # лишився один простий дільник у першому степені
        factors.append((n, 1))
    return factors

def lcm(a, b):
    return a // gcd(a, b) * b

def lambda_prime_power(p, k):
    """λ(p^k) для одного простого степеня — з аномалією двійки."""
    if p == 2:
        if k == 1: return 1         # λ(2)   = 1
        if k == 2: return 2         # λ(4)   = 2
        return 1 << (k - 2)         # λ(2^k) = 2^(k-2) для k ≥ 3
    return (p - 1) * p ** (k - 1)   # непарне просте: λ = φ(p^k)

def carmichael_lambda(n):
    """λ(n) = НСК по простих степенях розкладу n."""
    result = 1
    for p, k in factorize(n):
        result = lcm(result, lambda_prime_power(p, k))
    return result

assert carmichael_lambda(8)    == 2
assert carmichael_lambda(360)  == 12
assert carmichael_lambda(3233) == 780
