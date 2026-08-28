import math

RHO_WATER = 1000.0   # густина води, кг/м³
G = 9.81             # м/с²

def bisect(f, lo, hi, tol=1e-10, itmax=100):
    """Половинний поділ. f(lo) і f(hi) МУСЯТЬ мати різні знаки."""
    flo, fhi = f(lo), f(hi)
    if flo == 0.0: return lo
    if fhi == 0.0: return hi
    if (flo < 0) == (fhi < 0):
        raise ValueError("корінь не затиснутий: однакові знаки на кінцях")
    for _ in range(itmax):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if fm == 0.0 or 0.5 * (hi - lo) < tol:
            return mid
        if (flo < 0) == (fm < 0):
            lo, flo = mid, fm      # корінь у правій половині
        else:
            hi, fhi = mid, fm      # корінь у лівій половині
    return 0.5 * (lo + hi)

def sphere_submerged_volume(d, R):
    """Об'єм кульового сегмента висоти d: куля радіуса R занурена на глибину d."""
    d = min(max(d, 0.0), 2 * R)
    return math.pi * d * d * (R - d / 3.0)

def draft(rho_body, total_volume, submerged_volume, h_max):
    """Осадка d із рівноваги: витіснений об'єм = (ρ_тіла/ρ_води)·V_повний."""
    target = (rho_body / RHO_WATER) * total_volume
    return bisect(lambda d: submerged_volume(d) - target, 0.0, h_max)

R = 0.10                                    # радіус кулі, м
rho_body = 600.0                            # дерево, кг/м³
V_total = 4.0 / 3.0 * math.pi * R ** 3
d = draft(rho_body, V_total,
          lambda z: sphere_submerged_volume(z, R), h_max=2 * R)
print("осадка кулі: d = %.4f м" % d)        # → 0.1134 м
