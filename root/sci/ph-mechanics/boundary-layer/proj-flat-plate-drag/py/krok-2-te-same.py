from scipy.integrate import solve_ivp
from scipy.optimize import brentq

def rhs(eta, y):                       # y = [f, f′, f″]
    f, fp, fpp = y
    return [fp, fpp, -0.5 * f * fpp]

def miss(fpp0, eta_max=8.0):
    """Наскільки f′ на краю промахує повз 1 — цільова для коренешукача."""
    sol = solve_ivp(rhs, (0.0, eta_max), [0.0, 0.0, fpp0],
                    rtol=1e-10, atol=1e-12)
    return sol.y[1, -1] - 1.0

fpp0 = brentq(miss, 0.0, 1.0, xtol=1e-12)   # знайти корінь miss(s) = 0
print(f"f''(0) = {fpp0:.6f}")
