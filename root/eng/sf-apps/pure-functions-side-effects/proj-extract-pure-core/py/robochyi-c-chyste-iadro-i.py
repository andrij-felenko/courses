# ── ПІСЛЯ, частина 1: ЧИСТЕ ЯДРО ─────────────────────────────────
# вхід не мутуємо + Pricing явним аргументом + повернення значенням.
# Ніяких db/log/print/глобалей. Той самий вхід → той самий вихід, завжди.
def compute_totals(order: Order, p: Pricing) -> Totals:
    subtotal = 0.0
    for it in order.items:                     # читаємо вхід, не псуємо його
        subtotal += it.price * it.qty

    volume_disc = 0.0
    if   subtotal > 1000.0: volume_disc = 0.10
    elif subtotal >  300.0: volume_disc = 0.05

    tier_disc = 0.0
    if   order.customer_tier == "gold":   tier_disc = 0.08
    elif order.customer_tier == "silver": tier_disc = 0.04

    after_disc = subtotal * (1.0 - volume_disc) * (1.0 - tier_disc)
    taxed      = after_disc * (1.0 + p.tax_rate)
    shipping   = 0.0 if after_disc >= p.free_ship_from else p.ship_cost

    return Totals(
        subtotal,
        subtotal - after_disc,   # скільки всього знижено
        taxed - after_disc,      # сам податок
        shipping,
        taxed + shipping,        # підсумок
    )
