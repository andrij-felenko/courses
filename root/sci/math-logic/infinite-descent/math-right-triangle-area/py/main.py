from math import isqrt, gcd

def is_square(k):
    r = isqrt(k)
    return r * r == k

def descent_step(a, b, c):
    """Вхід: піфагорів трикутник a²+b²=c² із цілими сторонами,
    площа якого ab/2 — точний квадрат.
    Вихід: ТАКИЙ САМИЙ трикутник зі СТРОГО меншою гіпотенузою."""
    assert a > 0 and b > 0 and a*a + b*b == c*c
    assert (a * b) % 2 == 0 and is_square(a * b // 2)        # площа — цілий квадрат

    # 0. звести до примітивного: поділити катети на їхній спільний дільник
    d = gcd(a, b)
    a, b, c = a // d, b // d, c // d          # площа лишається квадратом (÷ d²)

    # 1. хай a — непарний катет, b — парний
    if a % 2 == 0:
        a, b = b, a
    # з a = m²−n², c = m²+n²:   m² = (c+a)/2,   n² = (c−a)/2
    m = isqrt((c + a) // 2)
    n = isqrt((c - a) // 2)
    assert m*m - n*n == a and 2*m*n == b and m*m + n*n == c

    # 2. площа = mn(m−n)(m+n); множники попарно взаємно прості,
    #    добуток — квадрат ⇒ кожен множник — квадрат
    p, q = isqrt(m), isqrt(n)
    r, s = isqrt(m + n), isqrt(m - n)
    assert p*p == m and q*q == n and r*r == m + n and s*s == m - n

    # 3. менший трикутник: катети (r+s)/2, (r−s)/2, гіпотенуза p
    U, V = (r + s) // 2, (r - s) // 2
    assert U*U + V*V == p*p                    # знову піфагорів трикутник
    assert is_square(U * V // 2)               # площа = n/4 = (q/2)² — знову квадрат
    assert p < c                               # гіпотенуза строго меншає

    return U, V, p
