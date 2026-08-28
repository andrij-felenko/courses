def iroot(s, n):
    """Ціла частина кореня n-го степеня з s — точно, лише на цілих."""
    if s < 2:
        return s
    hi = 1 << (-(-s.bit_length() // n))   # 2^⌈біти/n⌉ — завідомо не менше кореня
    lo = hi >> 1
    while lo < hi:                        # бінарний пошук найбільшого r: rⁿ ≤ s
        mid = (lo + hi + 1) >> 1
        if mid ** n <= s:
            lo = mid
        else:
            hi = mid - 1
    return lo

def search(n, N):
    """Прочесати 1 ≤ a ≤ b < N: розв'язок або найтісніший промах."""
    best = None                           # (відносний промах, a, b, cc, delta)
    for a in range(1, N):
        an = a ** n
        for b in range(a, N):
            s = an + b ** n
            c = iroot(s, n)               # cⁿ ≤ s < (c+1)ⁿ
            if c ** n == s:
                return f"РОЗВ'ЯЗОК: {a}^{n} + {b}^{n} = {c}^{n}"
            lo, hi = s - c ** n, (c + 1) ** n - s
            cc = c if lo < hi else c + 1   # найближчий n-й степінь
            delta = cc ** n - s            # >0: сума нижча за ccⁿ
            rel = abs(delta) / s
            if best is None or rel < best[0]:
                best = (rel, a, b, cc, delta)
    rel, a, b, cc, delta = best
    sign = "−" if delta > 0 else "+"
    return (f"немає розв'язку при a, b < {N};  найтісніше:  "
            f"{a}^{n} + {b}^{n} = {cc}^{n} {sign} {abs(delta)}")

print(search(3, 1000))
# немає розв'язку при a, b < 1000;  найтісніше:  791^3 + 812^3 = 1010^3 − 1
