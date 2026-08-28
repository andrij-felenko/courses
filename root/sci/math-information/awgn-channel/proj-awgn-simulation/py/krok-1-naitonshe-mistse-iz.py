import numpy as np
from math import erfc, sqrt

def q(x):
    """Q(x): імовірність, що стандартна гаусова величина перевищить x.
    Це просто хвіст нормального розподілу: Q(x) = ½·erfc(x/√2)."""
    return 0.5 * erfc(x / sqrt(2.0))

def noise_sigma(EbN0_dB, bits_per_symbol):
    """σ на КОЖНУ складову (I та Q) для символів одиничної енергії Es=1."""
    EbN0 = 10 ** (EbN0_dB / 10.0)          # з дБ у рази
    EsN0 = bits_per_symbol * EbN0          # Es = k·Eb  →  Es/N₀ = k·(Eb/N₀)
    N0 = 1.0 / EsN0                        # Es=1  →  N₀ = 1/(Es/N₀)
    return sqrt(N0 / 2.0)                  # σ² = N₀/2 на складову
