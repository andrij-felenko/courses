import numpy as np
from math import erf, erfc, sqrt, comb, log

rng = np.random.default_rng(20260719)

MU0, MU1 = -1.0, +1.0            # центри двох сусідніх рівнів (умовна напруга)
REF      = 0.5 * (MU0 + MU1)     # тверда опорна лінія — посередині, 0.0
HALF     = 0.5 * (MU1 - MU0)     # півпроміжок між рівнями, = 1.0

def Q(x):                        # хвіст стандартної нормалі: Q(x) = P(Z > x)
    return 0.5 * erfc(x / sqrt(2))

def q_inv(p):                    # обернена до Q, дихотомією
    lo, hi = 0.0, 15.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if Q(mid) > p else (lo, mid)
    return 0.5 * (lo + hi)

def sigma_for_rber(rber):        # RBER = Q(HALF/σ)  =>  σ = HALF / Q⁻¹(RBER)
    return HALF / q_inv(rber)
