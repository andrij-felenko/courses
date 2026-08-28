import math
from dataclasses import dataclass

@dataclass(frozen=True)
class Gas:
    """Стан середовища: густина, динамічна в'язкість, швидкість звуку."""
    rho: float                       # густина, кг/м³
    mu:  float                       # динамічна в'язкість, Па·с
    a:   float                       # швидкість звуку, м/с

    @property
    def nu(self) -> float:
        return self.mu / self.rho    # кінематична в'язкість ν, м²/с

# стандартна атмосфера на рівні моря, 15 °C
AIR   = Gas(rho=1.225, mu=1.789e-5, a=340.3)
# прісна вода, 20 °C
WATER = Gas(rho=998.2, mu=1.002e-3, a=1481.0)

def tunnel_speed(v_full, L_full, scale, flow=AIR, test=AIR):
    """Швидкість обдуву моделі, що зрівнює Re з оригіналом.
    scale = L_моделі / L_оригіналу  (модель 1:5 → scale = 0.2)."""
    L_model = scale * L_full
    v_model = v_full * (L_full / L_model) * (test.nu / flow.nu)
    Re      = flow.rho * v_full * L_full / flow.mu
    mach    = v_model / test.a
    return v_model, mach, Re
