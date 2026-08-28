# Той самий енергетичний баланс. Усе в СІ: фаради, вольти, ом → джоулі, секунди.
from dataclasses import dataclass

@dataclass
class ChargeBudget:
    w_src: float     # заплатило джерело
    w_cap: float     # осіло в конденсаторі
    w_heat: float    # згоріло в резисторі
    tau: float       # стала часу

def rc_charge_budget(C, V, R):
    return ChargeBudget(
        w_cap=0.5 * C * V * V,   # осіло в конденсаторі
        w_heat=0.5 * C * V * V,  # згоріло в резисторі — НЕ залежить від R
        w_src=C * V * V,         # заплатило джерело = сума двох вище
        tau=R * C,               # стала часу: лише вона залежить від R
    )

# rc_charge_budget(100e-6, 5.0, 100.0):
#   w_cap = w_heat = 1.25 мДж,  w_src = 2.5 мДж,  tau = 10 мс
