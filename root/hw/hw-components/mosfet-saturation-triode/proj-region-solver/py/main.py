from dataclasses import dataclass
from enum import Enum

class Region(Enum):
    CUTOFF     = "відсічка"
    TRIODE     = "тріод"
    SATURATION = "насичення"

@dataclass
class Mosfet:
    vth: float          # порогова напруга Vth, В
    k:   float          # крутість k = μ·Cox·W/L, А/В²
    lam: float = 0.0    # модуляція довжини каналу λ, 1/В (0 — ідеальна полиця)

def region(dev: Mosfet, vgs: float, vds: float) -> Region:
    """Чистий класифікатор: два порівняння, жодного струму."""
    vov = vgs - dev.vth              # перекриття (overdrive)
    if vov <= 0:
        return Region.CUTOFF         # канал не відкрито
    if vds < vov:
        return Region.TRIODE         # канал суцільний — резистор
    return Region.SATURATION         # стік защемлено — джерело струму
