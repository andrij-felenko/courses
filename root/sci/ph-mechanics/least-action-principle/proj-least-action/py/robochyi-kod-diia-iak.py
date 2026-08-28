import numpy as np

m, g = 1.0, 9.8               # маса (кг), тяжіння (м/с²)
T = 2.0                       # повний час польоту (с)
x_start, x_end = 0.0, 0.0     # закріплені кінці: старт і фініш на землі

def action(interior, dt):
    """Дискретна дія S = Σ (½m·vₖ² − m·g·x̄ₖ)·Δt для повного шляху з внутрішніх точок."""
    x = np.concatenate(([x_start], interior, [x_end]))
    v = np.diff(x) / dt                       # швидкість на кожному інтервалі
    kinetic   = 0.5 * m * v**2                # ½·m·v²
    potential = m * g * (x[:-1] + x[1:]) / 2  # m·g·x, усереднена по кінцях інтервалу
    return np.sum((kinetic - potential) * dt)
