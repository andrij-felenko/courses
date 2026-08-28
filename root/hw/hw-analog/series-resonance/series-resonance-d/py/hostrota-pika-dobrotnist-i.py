import math
from dataclasses import dataclass


# Добротність і смуга послідовного контуру на його f0.
# L у генрі, C у фарадах, R — повний послідовний опір втрат (Ом).
@dataclass
class Resonance:
    f0: float
    Q: float
    bw: float


def series_resonance(L, C, R):
    f0 = 1.0 / (2.0 * math.pi * math.sqrt(L * C))
    XL = 2.0 * math.pi * f0 * L                 # = Xc на резонансі
    Q = XL / R                                  # добротність
    bw = f0 / Q                                 # смуга −3 дБ
    return Resonance(f0, Q, bw)


# series_resonance(100e-6, 250e-12, 12.0) -> f0≈1 МГц, Q≈52, bw≈19 кГц
