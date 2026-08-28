from math import sqrt

# Затримка сигналу на доріжці плати (мікросмужка).
# len_m — довжина доріжки в метрах, eps_eff — ефективна проникність.
def trace_delay_ns(len_m, eps_eff):
    c = 2.998e8                    # м/с
    v = c / sqrt(eps_eff)          # швидкість у середовищі
    return (len_m / v) * 1e9       # у наносекундах

# приклад: 10 см на FR-4 → ≈0.56 нс
# d = trace_delay_ns(0.10, 2.8)
