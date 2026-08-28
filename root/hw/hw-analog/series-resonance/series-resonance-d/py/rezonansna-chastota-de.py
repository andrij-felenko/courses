import math


# Резонансна частота послідовного (чи паралельного) LC-контуру.
# L у генрі, C у фарадах; повертає частоту в герцах.
def resonant_freq(L, C):
    return 1.0 / (2.0 * math.pi * math.sqrt(L * C))


# resonant_freq(100e-6, 250e-12) -> ~1.0e6 Гц = 1 МГц
