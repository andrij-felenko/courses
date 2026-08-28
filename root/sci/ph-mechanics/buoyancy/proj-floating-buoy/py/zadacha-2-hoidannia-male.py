import numpy as np

def make_bob(rho_body, total_volume, waterplane_area):
    m = rho_body * total_volume
    omega2 = RHO_WATER * G * waterplane_area / m
    return omega2, 2 * np.pi / np.sqrt(omega2)      # (ω², аналітичний період)

Awp = math.pi * d * (2 * R - d)                     # площа на рівні води
omega2, T = make_bob(rho_body, V_total, Awp)

def accel(x):
    return -omega2 * x                              # притоплення → повертальна сила

def step_euler(x, v, h):                            # ЯВНИЙ Ейлер
    return x + v * h, v + accel(x) * h

def step_symplectic(x, v, h):                       # напівнеявний (Ейлер — Кромер)
    v = v + accel(x) * h                            # спершу швидкість…
    x = x + v * h                                   # …тоді координата за НОВОЮ швидкістю
    return x, v

def step_rk4(x, v, h):                              # Рунге — Кутта 4-го порядку
    def f(x, v): return v, accel(x)
    k1x, k1v = f(x, v)
    k2x, k2v = f(x + 0.5*h*k1x, v + 0.5*h*k1v)
    k3x, k3v = f(x + 0.5*h*k2x, v + 0.5*h*k2v)
    k4x, k4v = f(x + h*k3x,     v + h*k3v)
    x += h/6.0 * (k1x + 2*k2x + 2*k3x + k4x)
    v += h/6.0 * (k1v + 2*k2v + 2*k3v + k4v)
    return x, v

def simulate(step, x0, v0, h, steps):
    xs = [x0]
    x, v = x0, v0
    for _ in range(steps):
        x, v = step(x, v, h)
        xs.append(x)
    return np.array(xs)

def period_from_zeros(xs, h):
    """Період — середня відстань між висхідними перетинами нуля (з інтерполяцією)."""
    cross = [(i - 1 - xs[i-1] / (xs[i] - xs[i-1]))
             for i in range(1, len(xs))
             if xs[i-1] <= 0 < xs[i]]
    return float(np.mean(np.diff(cross))) * h

N = 60                       # кроків на період
h = T / N
steps = N * 12               # дванадцять періодів гойдання
x0 = 0.02                    # притопили на 2 см і відпустили

for name, step in [("Ейлер", step_euler),
                   ("симплектичний", step_symplectic),
                   ("RK4", step_rk4)]:
    xs = simulate(step, x0, 0.0, h, steps)
    print("%-13s T=%.5f с   амплітуда наприкінці %.3f м"
          % (name, period_from_zeros(xs, h), abs(xs[-N:]).max()))
print("%-13s T=%.5f с" % ("аналітичний", T))
