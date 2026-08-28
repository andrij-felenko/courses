# Викликати на КОЖЕН звіт від приймача.
#   fraction_lost — поле RTCP RR: 0..255, де 256 == 100% (floor(частка·256)).
# Повертає оновлений цільовий бітрейт (біт/с).
def abr_on_report(c: Abr, fraction_lost: int) -> int:
    # 0..255  →  проміле 0..1000:  ‰ = fraction_lost · 1000 / 256
    loss = (fraction_lost * 1000) >> 8

    if loss > c.loss_down_permille:
        # ── ЗОНА ПАДІННЯ: скидаємо тим різкіше, чим більші втрати ──
        # множник (1 − 0.5·p): за 10% → ×0.95, за 50% → ×0.75
        # у цілій арифметиці: rate · (2000 − loss) / 2000   (loss у ‰)
        num = 2000 - loss                      # напр., loss=300‰ → 1700
        c.rate = c.rate * num // 2000

    elif loss < c.loss_up_permille:
        # ── ЗОНА РОСТУ: один обережний крок угору ──
        c.rate += c.rate // 100 * c.up_step_pct   # +5%

    # ── інакше (2%..10%): МЕРТВА ЗОНА — нічого не міняємо ──

    # тримаємось у межах [rate_min, rate_max]
    c.rate = max(c.rate_min, min(c.rate, c.rate_max))

    return c.rate
