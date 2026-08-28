def annuity_factor(r, n):
    return float(n) if r == 0 else (1 - (1 + r) ** (-n)) / r

def solve_rate(target_A, n, lo=1e-9, hi=5.0, iters=100):
    """Знайти r*, за якої A(r*) = target_A. A спадає з r → бісекція надійна."""
    for _ in range(iters):
        mid = (lo + hi) / 2
        if annuity_factor(mid, n) > target_A:
            lo = mid        # A завелика → ставка замала → рухаємось управо
        else:
            hi = mid        # A замала  → ставка завелика → рухаємось уліво
    return (lo + hi) / 2

# «будувати» = «купити»:  150 + 20·A = 60·A  ⟹  A = 3.75
r_star = solve_rate(3.75, n=5)
print(f"r* = {r_star:.4f}  ({r_star * 100:.1f} %)")   # r* = 0.1042  (10.4 %)
