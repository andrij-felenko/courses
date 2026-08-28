# ── знімок політики: колишні глобальні змінні, тепер явний вхід ──
from dataclasses import dataclass

@dataclass
class Pricing:
    tax_rate:       float = 0.20
    free_ship_from: float = 500.0
    ship_cost:      float = 49.0

# ── результат: розкладка, а не голе число ──
@dataclass
class Totals:
    subtotal: float
    discount: float     # сума, на яку знижено
    tax:      float
    shipping: float
    total:    float
