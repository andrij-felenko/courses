from math import gcd

def totient(n: int) -> int:
    """φ(n) за формулою добутку: n·∏(1 − 1/p) по РІЗНИХ простих дільниках n."""
    result, m, p = n, n, 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:          # викидаємо всі копії p — показник не важить
                m //= p
            result -= result // p      # множимо на (1 − 1/p), не виходячи з цілих
        p += 1
    if m > 1:                          # лишився один великий простий дільник
        result -= result // m
    return result

assert totient(10) == 4
assert totient(360) == 96
assert totient(55) == 40

a, k, n = 7, 222, 10
assert gcd(a, n) == 1                  # без цього все нижче не має сили
print(pow(a, k % totient(n), n))       # 9 — звели показник: 222 mod 4 = 2
print(pow(a, k, n))                    # 9 — та сама відповідь довгою дорогою
