/* Крок ПІ-регулятора. err_ns — фазова помилка (нс).
 * Повертає поправку до коду ЦАП (ціле, зі знаком). */
static int32_t pi_step(pi_ctl_t *pi, int32_t err_ns, dac_status_t last_dac_st)
{
    /* --- Пропорційна частина: миттєва реакція --- */
    int64_t p_term = (int64_t)pi->kp * err_ns;     /* Q16 */

    /* --- Інтегральна частина з антивіндапом --- *
     * Знак узгоджено так: integ += ki·err (ki>0), тож ДОДАТНА помилка
     * штовхає інтеграл (і код) ВГОРУ, від'ємна — вниз. (Якщо на вашому
     * залізі полярність зворотна — тут і міняють знак ki, один раз.)
     * Умовне інтегрування (conditional integration) — найпростіший і
     * найнадійніший антивіндап: НЕ накопичувати в той бік, куди вихід
     * уже впертий; доки насичені, інтеграл у той бік стоїть. */
    bool railed_up   = (last_dac_st == DAC_RAILED_HIGH);
    bool railed_low  = (last_dac_st == DAC_RAILED_LOW);
    bool err_pushes_up   = (err_ns > 0);  /* додатна помилка тягне код вгору */
    bool err_pushes_down = (err_ns < 0);

    if (!(railed_up && err_pushes_up) && !(railed_low && err_pushes_down)) {
        pi->integ += (int64_t)pi->ki * err_ns;     /* звичайне накопичення */
    }
    /* Тверда межа інтеграла — друга страховка: навіть без railing
     * не даємо накопичувачу вилізти за фізично осмислений діапазон. */
    if (pi->integ > pi->integ_max) pi->integ = pi->integ_max;
    if (pi->integ < pi->integ_min) pi->integ = pi->integ_min;

    int64_t out_q16 = p_term + pi->integ;
    return (int32_t)(out_q16 >> 16);               /* Q16 → ціле, код ЦАП */
}
