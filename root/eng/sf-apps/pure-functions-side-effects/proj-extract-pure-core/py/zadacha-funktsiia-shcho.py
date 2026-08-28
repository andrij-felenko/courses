# ── ДО: одна функція робить усе ──────────────────────────────────
from dataclasses import dataclass, field

@dataclass
class Item:
    price: float
    qty: int

@dataclass
class Order:
    id: int
    customer_tier: str                       # "regular" | "silver" | "gold"
    items: list[Item] = field(default_factory=list)
    computed_total: float = 0.0              # ← сюди функція запише результат

# глобальний стан — прихований вхід, про який сигнатура мовчить
g_tax_rate       = 0.20
g_free_ship_from = 500.0
g_ship_cost      = 49.0

db  = Database()   # глобальне з'єднання з базою
log = Logger()     # глобальний лог

def compute_order_total(order: Order) -> float:   # order міняється на місці!
    subtotal = 0.0
    for it in order.items:
        subtotal += it.price * it.qty

    # знижка за обсяг
    volume_disc = 0.0
    if   subtotal > 1000.0: volume_disc = 0.10
    elif subtotal >  300.0: volume_disc = 0.05

    # знижка за рівень клієнта
    tier_disc = 0.0
    if   order.customer_tier == "gold":   tier_disc = 0.08
    elif order.customer_tier == "silver": tier_disc = 0.04

    # каскад: спершу обсяг, тоді рівень (множаться, не додаються)
    after_disc = subtotal * (1.0 - volume_disc) * (1.0 - tier_disc)

    # податок із глобального курсу
    taxed = after_disc * (1.0 + g_tax_rate)

    # доставка
    shipping = 0.0 if after_disc >= g_free_ship_from else g_ship_cost
    total    = taxed + shipping

    # ── а тепер ефекти, розсипані по функції ──
    order.computed_total = total                       # мутація входу
    db.save_total(order.id, total)                     # запис у базу
    log.info(f"order {order.id} total={total}")        # вивід у лог
    print(f"DEBUG total={total}")                      # ще й у консоль

    return total
