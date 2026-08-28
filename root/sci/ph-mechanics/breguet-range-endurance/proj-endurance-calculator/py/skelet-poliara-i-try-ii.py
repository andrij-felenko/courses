# -*- coding: utf-8 -*-
"""Калькулятор дальності й тривалості Бреге. Лише стандартна бібліотека."""
import math
from dataclasses import dataclass

# ── світові сталі ──
G      = 9.80665      # м/с² — стандартне прискорення вільного падіння
RHO_SL = 1.225        # кг/м³ — густина повітря біля моря (МСА)

@dataclass
class Polar:
    """Параболічна поляра опору  CD = CD0 + k·CL²  плюс площа крила."""
    CD0: float           # паразитне дно (форма, тертя, виступи)
    k:   float           # коефіцієнт індуктивного члена k·CL²
    S:   float           # площа крила, м²

    def CD(self, CL):    return self.CD0 + self.k * CL * CL
    def LD(self, CL):    return CL / self.CD(CL)

    def optima(self):
        """Три робочі коефіцієнти підйому — по одному на кожну мету."""
        CL_md = math.sqrt(self.CD0 / self.k)          # макс L/D:        k·CL² = CD0
        return {
            "md": CL_md,                              # мінімум опору / макс L/D
            "mp": math.sqrt(3.0) * CL_md,             # мінімум потужності (3·CD0)
            "jr": CL_md / math.sqrt(3.0),             # дальність струменя (CD0/3)
        }

    def speed(self, CL, W, rho=RHO_SL):
        """Швидкість горизонтального польоту: з L = W = ½·ρ·V²·S·CL."""
        return math.sqrt(2.0 * W / (rho * self.S * CL))
