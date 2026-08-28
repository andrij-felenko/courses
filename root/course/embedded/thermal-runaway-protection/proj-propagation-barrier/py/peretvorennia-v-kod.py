# Детектор події ПОШИРЕННЯ теплової втечі по пакету.
# Не плутати з тепловим foldback: цей модуль ловить ЛОКАЛЬНУ подію
# (одна зона злетіла на тлі холодних сусідів) і ухвалює незворотне рішення.
from enum import IntEnum
from dataclasses import dataclass, field

N_ZONES = 8            # теплових зон пакета (по давачу на зону)

# ── Пороги (десяті °C, де доречно). Підбирати під конкретний пакет. ──
LVL_TRIP_C10  = 1200   # 120.0 °C — зона явно в утечі (не просто гаряча)
RATE_TRIP     = 80     # 8.0 °C/с — крутий розгін (десятих °C за секунду)
SPREAD_TRIP   = 600    # 60.0 °C — зона настільки гарячіша за медіану зон
PERSIST_TICKS = 2      # підтвердити N послідовних тиків (проти одиничного збою)

class PropState(IntEnum):
    IDLE    = 0
    SUSPECT = 1
    LATCHED = 2

@dataclass
class PropDetector:
    state: PropState = PropState.IDLE
    prev_c10: list = field(default_factory=lambda: [0] * N_ZONES)  # для dT/dt
    suspect_cnt: int = 0          # скільки тиків поспіль бачимо підозру
    hot_zone: int = -1            # індекс зони-винуватця (для логів і вентиляції)
    have_prev: bool = False       # чи вже є попередній замір
