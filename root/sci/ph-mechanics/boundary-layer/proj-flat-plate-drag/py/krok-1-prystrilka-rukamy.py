import numpy as np

def blasius_rhs(state):
    """state = [f, f′, f″]  →  [f′, f″, f‴],  де f‴ = −½·f·f″."""
    f, fp, fpp = state
    return np.array([fp, fpp, -0.5 * f * fpp])

def rk4_step(state, h):
    k1 = blasius_rhs(state)
    k2 = blasius_rhs(state + 0.5 * h * k1)
    k3 = blasius_rhs(state + 0.5 * h * k2)
    k4 = blasius_rhs(state + h * k3)
    return state + (h / 6.0) * (k1 + 2*k2 + 2*k3 + k4)

def f_prime_at_infinity(fpp0, eta_max=8.0, h=0.005):
    """Проінтегрувати з f″(0)=fpp0 і повернути f′ на далекому краю."""
    state = np.array([0.0, 0.0, fpp0])
    for _ in range(int(eta_max / h)):
        state = rk4_step(state, h)
    return state[1]

def solve_blasius(eta_max=8.0, h=0.005, tol=1e-10):
    """Пристрілка бісекцією по f″(0), поки f′(η_max) → 1."""
    lo, hi = 0.0, 1.0
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if f_prime_at_infinity(mid, eta_max, h) > 1.0:
            hi = mid          # переліт → нахил завеликий, опускаємо стелю
        else:
            lo = mid          # недоліт → замалий, піднімаємо підлогу
    return 0.5 * (lo + hi)

fpp0 = solve_blasius()
print(f"f''(0) = {fpp0:.6f}")
