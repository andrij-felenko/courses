import cmath
from dataclasses import dataclass

K_BOLTZ = 1.380649e-23
T0      = 290.0
FOUR_KT = 4.0 * K_BOLTZ * T0             # 4kT₀ ≈ 1.6e-20

@dataclass
class NoiseParams:
    Fmin: float
    Rn:   float
    Gopt: float
    Bopt: float

# З двох вхідних джерел (en, in) та їх кореляції c — чотири шумові параметри.
# en у В/√Гц, in у А/√Гц, c безрозмірний комплексний (|c| ≤ 1).
def noise_params(en: float, i_n: float, c: complex) -> NoiseParams:
    en2 = en * en                        # ⟨|en|²⟩  (густина потужності напруги)
    in2 = i_n * i_n                      # ⟨|in|²⟩  (густина потужності струму)

    Rn = en2 / FOUR_KT                   # шумовий опір з напруги

    # провідність кореляції: Yc = c · (in/en)  (відношення модулів × фаза c)
    Yc = c * (i_n / en)
    Gc, Bc = Yc.real, Yc.imag

    # некорельована частка струму: потужність × (1 − |c|²) → провідність Gu
    in2_uncorr = in2 * (1.0 - abs(c)**2)
    Gu = in2_uncorr / FOUR_KT

    Bopt = -Bc                                   # компенсуємо реактивну кореляцію
    Gopt = cmath.sqrt(Gc*Gc + Gu / Rn).real      # геометричне серединне двох механізмів
    Fmin = 1.0 + 2.0 * Rn * (Gopt + Gc)          # дно чаші (у разах)
    return NoiseParams(Fmin, Rn, Gopt, Bopt)

# виклик:
en  = 0.45e-9                            # 0.45 нВ/√Гц
i_n = 4.0e-12                            # 4.0 пА/√Гц
c   = 0.2 + 0.3j                         # кореляція
p = noise_params(en, i_n, c)
# p.Rn ≈ 12.6 Ом
# p.Gopt ≈ 8.48 мСм,  p.Bopt ≈ −2.67 мСм   →  Yopt ≈ (8.48 − j2.67) мСм
# p.Fmin ≈ 1.259 разів  →  10·log10 ≈ 1.00 дБ
