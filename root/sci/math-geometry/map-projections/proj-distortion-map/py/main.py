import math, statistics

R = 6371008.8                      # середній радіус WGS-84, м
D = math.pi / 180

def tissot(f, phi, lam, h=1e-6):
    """Головні масштаби a, b, коефіцієнт площі a·b і кутова деформація ω (градуси)."""
    (xe1, ye1), (xe2, ye2) = f(phi, lam + h), f(phi, lam - h)   # СХІД — перший стовпець
    (xn1, yn1), (xn2, yn2) = f(phi + h, lam), f(phi - h, lam)   # ПІВНІЧ — другий
    de, dn = 2 * h * R * math.cos(phi), 2 * h * R               # метрів по землі

    m11, m12 = (xe1 - xe2) / de, (xn1 - xn2) / dn
    m21, m22 = (ye1 - ye2) / de, (yn1 - yn2) / dn

    E, F = (m11 + m22) / 2, (m11 - m22) / 2
    G, H = (m21 + m12) / 2, (m21 - m12) / 2
    Q, S = math.hypot(E, H), math.hypot(F, G)

    a, b = Q + S, abs(Q - S)
    lo, hi = min(Q, S), max(Q, S)
    omega = math.degrees(2 * math.asin(min(1.0, lo / hi))) if hi > 0 else 0.0
    return a, b, a * b, omega

def sweep(f, south, west, north, east, n=61):
    """Найгірше й медіанне спотворення по сітці над прямокутником (градуси)."""
    area, omega = [], []
    for i in range(n):
        phi = (south + (north - south) * i / (n - 1)) * D
        for j in range(n):
            lam = (west + (east - west) * j / (n - 1)) * D
            _, _, ab, om = tissot(f, phi, lam)
            area.append(ab)
            omega.append(om)
    med = statistics.median(area)          # калібрування номінального масштабу карти
    return (min(area) / med, max(area) / med, max(omega), statistics.median(omega))

def mercator(lam0):
    return lambda phi, lam: (R * (lam - lam0), R * math.asinh(math.tan(phi)))

def lambert_cea(phi1, lam0):               # циліндрична рівновелика, нормальна паралель phi1
    c = math.cos(phi1)
    return lambda phi, lam: (R * (lam - lam0) * c, R * math.sin(phi) / c)

def lambert_cc(phi1, phi2, phi0, lam0):    # конічна конформна на двох стандартних паралелях
    t = lambda p: math.tan(math.pi / 4 + p / 2)
    n = math.log(math.cos(phi1) / math.cos(phi2)) / math.log(t(phi2) / t(phi1))
    F = math.cos(phi1) * t(phi1) ** n / n
    rho0 = R * F / t(phi0) ** n
    def f(phi, lam):
        rho, th = R * F / t(phi) ** n, n * (lam - lam0)
        return (rho * math.sin(th), rho0 - rho * math.cos(th))
    return f

def azimuthal_ed(phi0, lam0):              # азимутальна рівнопроміжна з центром (phi0, lam0)
    def f(phi, lam):
        cc = (math.sin(phi0) * math.sin(phi)
              + math.cos(phi0) * math.cos(phi) * math.cos(lam - lam0))
        c = math.acos(max(-1.0, min(1.0, cc)))       # кутова відстань від центра
        k = 1.0 if c < 1e-10 else c / math.sin(c)
        return (R * k * math.cos(phi) * math.sin(lam - lam0),
                R * k * (math.cos(phi0) * math.sin(phi)
                         - math.sin(phi0) * math.cos(phi) * math.cos(lam - lam0)))
    return f
