import cmath
import math

def coil_impedance(R, L, f):
    """імпеданс реальної котушки на частоті f"""
    w = 2.0 * math.pi * f          # кутова частота ω
    return complex(R, w * L)       # Z = R + j*(ω·L)

# приклад: R=30 Ом, L=10 мГн, f=400 Гц
Z = coil_impedance(30.0, 0.010, 400.0)

mag   = abs(Z)                     # |Z| ≈ 39.1 Ом
phase = cmath.phase(Z)             # φ  ≈ 0.696 рад ≈ 39.9°
I     = 12.0 / mag                 # амплітуда струму ≈ 0.307 А
