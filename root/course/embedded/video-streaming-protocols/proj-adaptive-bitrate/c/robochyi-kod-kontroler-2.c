// Викликати на КОЖЕН звіт від приймача.
//   fraction_lost — поле RTCP RR: 0..255, де 256 == 100% (floor(частка·256)).
// Повертає оновлений цільовий бітрейт (біт/с).
uint32_t abr_on_report(abr_t *c, uint8_t fraction_lost)
{
    // 0..255  →  проміле 0..1000:  ‰ = fraction_lost · 1000 / 256
    uint16_t loss = (uint16_t)(((uint32_t)fraction_lost * 1000u) >> 8);

    if (loss > c->loss_down_permille) {
        // ── ЗОНА ПАДІННЯ: скидаємо тим різкіше, чим більші втрати ──
        // множник (1 − 0.5·p): за 10% → ×0.95, за 50% → ×0.75
        // у цілій арифметиці: rate · (2000 − loss) / 2000   (loss у ‰)
        uint32_t num = 2000u - loss;           // напр., loss=300‰ → 1700
        c->rate = (uint32_t)(((uint64_t)c->rate * num) / 2000u);

    } else if (loss < c->loss_up_permille) {
        // ── ЗОНА РОСТУ: один обережний крок угору ──
        c->rate += c->rate / 100u * c->up_step_pct;   // +5%

    }
    // ── інакше (2%..10%): МЕРТВА ЗОНА — нічого не міняємо ──

    // тримаємось у межах [rate_min, rate_max]
    if (c->rate < c->rate_min) c->rate = c->rate_min;
    if (c->rate > c->rate_max) c->rate = c->rate_max;

    return c->rate;
}
