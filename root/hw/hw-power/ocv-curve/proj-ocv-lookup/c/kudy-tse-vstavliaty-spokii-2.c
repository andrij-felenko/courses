typedef struct {
    uint16_t soc_pm;     // поточна оцінка заряду (веде лічильник струму)
    uint32_t var_pm2;    // її дисперсія, проміле²
} soc_state_t;

#define VAR_RATE_PM2_PER_H   64u          // за годину лічильник додає σ ≈ 0.8 %
#define VAR_CEIL_PM2       (250u * 250u)  // далі рости нема сенсу: σ = 25 %

// Недовіра до лічильника росте, поки його ніхто не виправляє: за моделлю
// випадкового блукання дисперсія додається лінійно з часом (σ — як корінь).
void soc_age(soc_state_t *s, uint32_t dt_ms) {
    uint32_t grow = (uint32_t)((uint64_t)VAR_RATE_PM2_PER_H * dt_ms / 3600000u);
    s->var_pm2 = (s->var_pm2 + grow < VAR_CEIL_PM2) ? s->var_pm2 + grow : VAR_CEIL_PM2;
}

bool soc_apply_ocv(soc_state_t *s, ocv_read_t r) {
    if (!r.usable || s->var_pm2 == 0) return false;   // сліпа таблиця або бездоганний лічильник

    uint32_t var_o = (uint32_t)r.sigma_pm * (uint32_t)r.sigma_pm;
    uint32_t var_c = s->var_pm2;

    // Вага у форматі Q16. Чисельник var_c·65536 сягає 4.1·10⁹ — це вже за стелю
    // int32 і впритул до стелі uint32, тож проміжок беремо 64-бітний.
    // Це разова дія на подію спокою, не гарячий шлях: коштувати може будь-що.
    uint32_t w_q16 = (uint32_t)(((uint64_t)var_c << 16) / (var_c + var_o));

    int32_t err  = (int32_t)r.soc_pm - (int32_t)s->soc_pm;
    int32_t corr = (int32_t)(((int64_t)err * (int64_t)w_q16) / 65536);   // ділення, не зсув

    int32_t soc = (int32_t)s->soc_pm + corr;
    s->soc_pm   = (uint16_t)(soc < 0 ? 0 : (soc > 1000 ? 1000 : soc));
    s->var_pm2  = (uint32_t)(((uint64_t)(65536u - w_q16) * var_c) / 65536);
    return true;
}
