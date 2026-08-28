import math

def rationalize(r, max_den=32):
    """Найкращий дріб p/q ≈ r зі знаменником не більшим за max_den (r > 0).
    Підхідні дроби: кожен наступний = a·попередній + той, що був перед ним."""
    h_prev, h = 0, 1                  # чисельники двох останніх підхідних дробів
    k_prev, k = 1, 0                  # їхні знаменники
    v = r
    for _ in range(64):
        a = math.floor(v)
        h_prev, h = h, a * h + h_prev
        k_prev, k = k, a * k + k_prev
        if k > max_den:               # знаменник переріс межу — беремо попередній дріб
            return h_prev, k_prev
        rem = v - a
        if rem < 1e-12:               # розклад скінчився: дріб точний
            return h, k
        v = 1.0 / rem
    return h, k


def common_period(fx, fy, max_den=64):
    """Час, за який замикається фігура: T = p/fx = q/fy."""
    p, q = rationalize(fx / fy, max_den)
    return p / fx, p, q
