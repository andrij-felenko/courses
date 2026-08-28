/* Статус railing останнього запису ЦАП — місток до антивіндапу. */
static dac_status_t g_last_dac_status = DAC_OK;

void gpsdo_tick_1s(pi_ctl_t *pi, holdover_t *h)
{
    pps_sample_t s = pps_read();
    static int64_t integ_prev;

    if (s.valid && pps_sane(s.phase_err_ns)) {
        /* --- Є GPS: нормальна дисципліна --- */
        if (h->mode == MODE_HOLDOVER) {
            /* Повернувся GPS. НЕ стрибати різко: увійти в lock плавно,
             * лишивши інтеграл як є — фаза сама підтягнеться повільною петлею. */
            h->mode = MODE_LOCKED;
            h->hold_seconds = 0;
        }
        dac_status_t st = g_last_dac_status;      /* railing з минулого запису */
        int32_t trim = pi_step(pi, s.phase_err_ns, st);  /* повний код поправки GPS */

        drift_learn(h, pi->integ, integ_prev);    /* учимо швидкість дрейфу */
        integ_prev = pi->integ;
        if (h->locked_seconds < 0xFFFFFFFF) h->locked_seconds++;

        gpsdo_apply(trim);                        /* поправка GPS → суматор → ЦАП */

    } else {
        /* --- GPS зник: holdover --- */
        if (h->mode == MODE_LOCKED) {
            /* Щойно ввійшли: зафіксувати поправку. Довіряти вивченому
             * дрейфу лише якщо lock тривав достатньо довго, щоб його оцінити. */
            h->mode = MODE_HOLDOVER;
            h->integ_hold = pi->integ;
            h->hold_seconds = 0;
            if (h->locked_seconds < 3600) h->drift_rate_q16 = 0; /* мало вчились — не екстраполюємо */
        }
        h->hold_seconds++;

        /* Екстраполяція: продовжуємо рухати поправку з вивченою швидкістю.
         * П-складової тут немає — фази ж нема; лишається сам інтеграл. */
        int64_t predicted = h->integ_hold
                          + (h->drift_rate_q16 * (int64_t)h->hold_seconds >> 16);
        pi->integ = predicted;                    /* тримаємо петлю в курсі */
        gpsdo_apply((int32_t)(predicted >> 16));  /* інтеграл (Q16) → код поправки */

        fault_set(FAULT_HOLDOVER);                /* сигнал: працюємо без GPS */
    }
}
