import cmath, math

# Коефіцієнт шуму за провідністю джерела (формула Роте — Дальке).
# Fmin задано в РАЗАХ (не дБ); провідності — у сименсах.
def noise_factor(Fmin, Rn, Yopt, Ys):
    Gs = Ys.real                        # дійсна частина провідності джерела
    d = Ys - Yopt                       # відхід від оптимуму
    dist2 = abs(d)**2                   # |Ys − Yopt|²
    return Fmin + (Rn / Gs) * dist2

# 0.6 дБ у разах:  10^(0.6/10) = 1.148
Fmin = 1.148
Rn   = 30.0
Yopt = 8e-3  - 6e-3j                    # (8 − j6) мСм
Ys   = 12e-3 - 2e-3j                    # (12 − j2) мСм

F  = noise_factor(Fmin, Rn, Yopt, Ys)  # ≈ 1.228 (разів)
dB = 10.0 * math.log10(F)              # ≈ 0.89 дБ
