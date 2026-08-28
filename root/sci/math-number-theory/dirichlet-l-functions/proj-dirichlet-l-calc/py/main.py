import cmath
import math

def find_primitive_root(p: int) -> int:
    if p == 2:
        return 1
    phi = p - 1
    factors = []
    n = phi
    d = 2
    while d * d <= n:
        if n % d == 0:
            factors.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        factors.append(n)

    for res in range(2, p):
        ok = True
        for f in factors:
            if pow(res, phi // f, p) == 1:
                ok = False
                break
        if ok:
            return res
    return -1

def compute_dirichlet_l(p: int, char_m: int, g: int, s: complex, n_terms: int) -> complex:
    # Таблиця дискретного логарифма ind_g(a)
    log_table = {}
    cur = 1
    for k in range(p - 1):
        log_table[cur] = k
        cur = (cur * g) % p

    l_sum = 0.0 + 0.0j
    phi_p = p - 1

    for n in range(1, n_terms + 1):
        rem = n % p
        if rem == 0 or math.gcd(rem, p) > 1:
            continue
        k = log_table[rem]
        angle = 2.0 * math.pi * char_m * k / phi_p
        chi_val = cmath.rect(1.0, angle)
        n_s = n ** (-s)
        l_sum += chi_val * n_s

    return l_sum

if __name__ == "__main__":
    p = 5
    g = find_primitive_root(p)
    print(f"Модуль p = {p}, Первісний корінь g = {g}\n")

    s_point = 1.0 + 0.0j
    n_terms = 100000

    for m in range(p - 1):
        l_res = compute_dirichlet_l(p, m, g, s_point, n_terms)
        print(f"Характер chi_{m}: L(1, chi) = {l_res.real:.6f} + {l_res.imag:.6f}j (модуль = {abs(l_res):.6f})")
