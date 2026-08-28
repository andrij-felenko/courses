typedef enum { MODE_LOCKED, MODE_HOLDOVER } gpsdo_mode_t;

typedef struct {
    gpsdo_mode_t mode;
    int64_t      integ_hold;      /* поправка на момент входу в holdover */
    int64_t      drift_rate_q16;  /* вивчена швидкість дрейфу (код/с, Q16) */
    uint32_t     hold_seconds;    /* скільки вже триває holdover */
    uint32_t     locked_seconds;  /* скільки тримали lock (для достовірності) */
} holdover_t;

/* Дуже повільна оцінка швидкості дрейфу, поки ми в LOCKED.
 * Це фільтрована похідна інтеграла: наскільки поправка «повзе» за секунду.
 * alpha МАЛЕНЬКА (напр. 1/4096) — оцінка має усереднюватись годинами. */
static void drift_learn(holdover_t *h, int64_t integ_now, int64_t integ_prev)
{
    int64_t delta = integ_now - integ_prev;                 /* приріст за 1 с */
    /* експоненційне згладжування: rate += (delta − rate)·alpha */
    h->drift_rate_q16 += (delta - h->drift_rate_q16) >> 12;  /* alpha ≈ 1/4096 */
}
