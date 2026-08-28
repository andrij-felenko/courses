import math

def solve_kepler(M, e, tol=1e-12, max_iter=100):
    """M = E − e·sinE  →  E.  Робастний старт E₀ = π для великих e (комети)."""
    M %= 2 * math.pi                        # звести M у [0, 2π)
    flip = M > math.pi
    if flip:                                # симетрія E(2π−M) = 2π − E(M): рахуємо на [0, π]
        M = 2 * math.pi - M
    E = math.pi if e > 0.8 else M + e * math.sin(M)     # початкове наближення
    for _ in range(max_iter):
        dE = (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
        E -= dE
        if abs(dE) < tol:                   # квадратична збіжність: зазвичай 3–6 кроків
            break
    return 2 * math.pi - E if flip else E

def orbit_xy(a, e, T, t, t0=0.0):
    """Координати (x, y) відносно Сонця; +x — на перигелій, +y — за рухом планети."""
    M = 2 * math.pi * (t - t0) / T          # середня аномалія: росте лінійно з часом
    E = solve_kepler(M, e)
    x = a * (math.cos(E) - e)
    y = a * math.sqrt(1 - e * e) * math.sin(E)
    return x, y

# Приклад: Марс через 100 діб після перигелію
a, e, T = 1.524, 0.0934, 686.98             # а.о., —, діб
x, y = orbit_xy(a, e, T, t=100.0)
r  = math.hypot(x, y)
nu = math.degrees(math.atan2(y, x))         # істинна аномалія; правильна чверть — саме через atan2
print(f"x={x:.4f}  y={y:.4f}  r={r:.4f} а.о.  ν={nu:.2f}°")
# → x=0.6902  y=1.2709  r=1.4462 а.о.  ν=61.49°
