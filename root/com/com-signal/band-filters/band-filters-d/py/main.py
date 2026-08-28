# notch на f0 за частоти дискретизації fs і добротності Q → коеф. біквада
import math
from dataclasses import dataclass


@dataclass
class Biquad:  # вже нормовані на a0
    b0: float
    b1: float
    b2: float
    a1: float
    a2: float


def design_notch(f0: float, fs: float, Q: float) -> Biquad:
    w0    = 2.0 * math.pi * f0 / fs   # 2π·50/1000 ≈ 0.3142 рад/відлік
    cosw0 = math.cos(w0)
    alpha = math.sin(w0) / (2.0 * Q)  # sin(w0)/(2·12.5) — задає ширину

    a0 = 1.0 + alpha                  # спільний знаменник
    return Biquad(                    # b1 == a1 — прикмета саме notch
        b0=1.0          / a0,         # у чисельнику: s² + 1
        b1=(-2.0*cosw0) / a0,
        b2=1.0          / a0,
        a1=(-2.0*cosw0) / a0,         # зворотний зв'язок
        a2=(1.0 - alpha)/ a0,
    )
