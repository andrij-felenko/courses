import math
import random
import cmath

def mod_exp(base: int, exp: int, mod: int) -> int:
    return pow(base, exp, mod)

def apply_inverse_qft(state: list[complex]) -> list[complex]:
    q = len(state)
    out = [complex(0, 0)] * q
    inv_sqrt_q = 1.0 / math.sqrt(q)
    two_pi = 2.0 * math.pi

    for y in range(q):
        s = complex(0, 0)
        for x in range(q):
            angle = -two_pi * (x * y) / q
            s += state[x] * cmath.exp(complex(0, angle))
        out[y] = s * inv_sqrt_q
    return out

def continued_fraction_convergents(y: int, q: int, n: int) -> list[int]:
    candidates = []
    a_num, a_den = y, q
    p_prev2, p_prev1 = 0, 1
    q_prev2, q_prev1 = 1, 0

    while a_den != 0:
        quot = a_num // a_den
        rem = a_num % a_den

        p_curr = quot * p_prev1 + p_prev2
        q_curr = quot * q_prev1 + q_prev2

        if q_curr >= n:
            break
        if q_curr > 0:
            candidates.append(q_curr)

        p_prev2, p_prev1 = p_prev1, p_curr
        q_prev2, q_prev1 = q_prev1, q_curr
        a_num, a_den = a_den, rem

    return candidates

def quantum_find_period(a: int, n: int) -> int | None:
    m = 1
    while (1 << m) < n * n:
        m += 1
    q = 1 << m

    x0 = random.randint(0, n - 1)
    target_val = mod_exp(a, x0, n)

    state = [complex(0, 0)] * q
    count = 0
    for x in range(q):
        if mod_exp(a, x, n) == target_val:
            state[x] = complex(1, 0)
            count += 1

    if count == 0:
        return None

    norm = 1.0 / math.sqrt(count)
    state = [s * norm for s in state]

    transformed = apply_inverse_qft(state)
    probs = [abs(c) ** 2 for c in transformed]

    measured_y = random.choices(range(q), weights=probs, k=1)[0]
    if measured_y == 0:
        return None

    for cand_r in continued_fraction_convergents(measured_y, q, n):
        if cand_r > 1 and mod_exp(a, cand_r, n) == 1:
            return cand_r
    return None

def shor_factorize(n: int) -> tuple[int, int]:
    if n % 2 == 0:
        return 2, n // 2

    for _ in range(100):
        a = random.randint(2, n - 2)
        g = math.gcd(a, n)
        if g > 1:
            return g, n // g

        r = quantum_find_period(a, n)
        if r is None or r % 2 != 0:
            continue

        half_pow = mod_exp(a, r // 2, n)
        if half_pow == n - 1:
            continue

        f1 = math.gcd(half_pow - 1, n)
        f2 = math.gcd(half_pow + 1, n)

        if 1 < f1 < n:
            return f1, n // f1
        if 1 < f2 < n:
            return f2, n // f2

    return 1, n

if __name__ == "__main__":
    n = 15
    p, q = shor_factorize(n)
    print(f"Факторизація N = {n} -> {p} * {q}")
