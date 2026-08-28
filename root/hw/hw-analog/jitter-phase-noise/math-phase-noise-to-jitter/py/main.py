import math
from dataclasses import dataclass

# Одна горизонтальна ділянка маски фазового шуму.
@dataclass
class PnSegment:
    f_lo: float    # нижня межа відступу, Гц
    f_hi: float    # верхня межа відступу, Гц
    L_dbc: float   # рівень L(f) на ділянці, дБн/Гц

# Інтегрований RMS-джиттер у секундах за кусково-плоскою маскою.
# f0 — несуча, Гц;  mask — ділянки маски в робочій смузі.
def integrated_jitter_s(f0, mask):
    var_phi = 0.0                                  # дисперсія фази, рад²
    for seg in mask:
        dens  = 10.0 ** (seg.L_dbc / 10.0)         # дБн/Гц → рази
        width = seg.f_hi - seg.f_lo                # ширина ділянки, Гц
        var_phi += dens * width                    # площа прямокутника
    var_phi *= 2.0                                 # однобічна L → повна щільність фази
    sigma_phi = math.sqrt(var_phi)                 # RMS фази, рад
    return sigma_phi / (2.0 * math.pi * f0)        # → секунди

# Маска нашого джерела 100 МГц у смузі 12 кГц…20 МГц.
mask = [
    PnSegment(12.0e3,  100.0e3, -120.0),
    PnSegment(100.0e3,   1.0e6, -135.0),
    PnSegment(  1.0e6,  20.0e6, -150.0),
]

f0 = 100.0e6
tj = integrated_jitter_s(f0, mask)
# var_phi(до×2) = 1e-12·88e3 + 3.162e-14·900e3 + 1e-15·19e6
#              = 8.80e-8 + 2.85e-8 + 1.90e-8 = 1.355e-7
# ×2 = 2.710e-7 рад²;  √ = 5.206e-4 рад;  /(2π·1e8) = 8.29e-13 с ≈ 0.83 пс
