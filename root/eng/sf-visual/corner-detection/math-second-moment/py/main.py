from math import sqrt
from typing import NamedTuple

class M2(NamedTuple):
    Sxx: float
    Syy: float
    Sxy: float

def classify(name, m):
    det   = m.Sxx * m.Syy - m.Sxy * m.Sxy   # λ1·λ2
    trace = m.Sxx + m.Syy                    # λ1+λ2
    harris = det - 0.05 * trace * trace      # відгук Гарріса
    # менше власне число = min(λ1, λ2):
    disc = sqrt(trace * trace * 0.25 - det)
    lmin = trace * 0.5 - disc                # Ші–Томасі
    print(f"{name:<8} det={det:8.1f} trace={trace:7.1f}  "
          f"Harris={harris:9.1f}  min(lam)={lmin:6.1f}")

classify("рівне", M2(  5.,   4.,  1.))  # обидва градієнти кволі
classify("край",  M2(900.,   6., 70.))  # сильний лише по x
classify("кут",   M2(800., 650., 90.))  # сильний по обох осях
