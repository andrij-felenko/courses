import math
from dataclasses import dataclass


# Повна картина послідовного RLC-резонансу з L, C, R.
# L у генрі, C у фарадах, R — повний послідовний опір втрат (Ом).
@dataclass
class Resonance:
    w0: float   # кутова резонансна частота, рад/с
    f0: float   # резонансна частота, Гц
    X0: float   # реактивний опір елемента на резонансі (XL = Xc), Ом
    Q: float    # добротність
    bw: float   # смуга −3 дБ, Гц


def series_rlc(L, C, R):
    w0 = 1.0 / math.sqrt(L * C)              # ω₀ = 1/√(LC)
    f0 = w0 / (2.0 * math.pi)
    X0 = w0 * L                              # = 1/(ω₀C) на резонансі
    Q = X0 / R                               # Q = ω₀L/R
    bw = f0 / Q                              # Δf = f₀/Q = R/(2πL)
    return Resonance(w0, f0, X0, Q, bw)


# Точне значення |Z| на ДОВІЛЬНІЙ частоті — те, з чого все виведено.
def z_mag(L, C, R, w):
    X = w * L - 1.0 / (w * C)                # реактивність XL − Xc
    return math.sqrt(R * R + X * X)          # |Z| = √(R² + X²)


L, C, R, U = 100e-6, 250e-12, 12.0, 1.0
r = series_rlc(L, C, R)

Imax = U / R                                 # струм на резонансі
Umag = r.Q * U                               # напруга на L і C: Q·U

print(f"f0   = {r.f0 / 1e6:.3f} МГц")
print(f"|Z|0 = {z_mag(L, C, R, r.w0):.1f} Ом  (= R, мінімум)")
print(f"Imax = {Imax * 1000.0:.0f} мА")
print(f"X0   = {r.X0:.0f} Ом   (XL = Xc на резонансі)")
print(f"Q    = {r.Q:.1f}")
print(f"U_L = U_C = {Umag:.1f} В   (з U = {U:.0f} В на вході)")
print(f"смуга −3 дБ = {r.bw / 1e3:.1f} кГц")
# Очікуваний вивід:
#    f0   = 1.006 МГц
#    |Z|0 = 12.0 Ом  (= R, мінімум)
#    Imax = 83 мА
#    X0   = 632 Ом   (XL = Xc на резонансі)
#    Q    = 52.7
#    U_L = U_C = 52.7 В   (з U = 1 В на вході)
#    смуга −3 дБ = 19.1 кГц
