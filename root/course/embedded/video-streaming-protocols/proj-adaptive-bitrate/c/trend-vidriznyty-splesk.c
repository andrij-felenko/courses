typedef struct {
    abr_t    base;          // контролер із гістерезисом (вище)
    uint16_t loss_avg;      // згладжені втрати, ‰  (EMA)
    uint32_t jitter_avg;    // згладжений джитер (одиниці RTP timestamp)
    uint8_t  alpha_pct;     // вага нового звіту в EMA, %  (напр., 25 → α=0.25)
    uint8_t  seeded;        // 0 до першого звіту: EMA треба засіяти, не зростати з нуля
} abr_trend_t;

void abr_trend_init(abr_trend_t *t, uint32_t start, uint32_t lo, uint32_t hi)
{
    abr_init(&t->base, start, lo, hi);
    t->loss_avg   = 0;
    t->jitter_avg = 0;
    t->alpha_pct  = 25;    // α = 0.25: розумний баланс глушіння й чуйності
    t->seeded     = 0;     // перший звіт сяде в середнє цілком, без розгону з 0
}

// EMA в цілій арифметиці:  avg += α·(нове − avg)
static uint16_t ema_u16(uint16_t avg, uint16_t sample, uint8_t alpha_pct)
{
    int32_t d = (int32_t)sample - (int32_t)avg;
    return (uint16_t)((int32_t)avg + d * (int32_t)alpha_pct / 100);
}

uint32_t abr_trend_on_report(abr_trend_t *t,
                             uint8_t  fraction_lost,
                             uint32_t jitter)
{
    uint16_t loss = (uint16_t)(((uint32_t)fraction_lost * 1000u) >> 8);

    // 0) перший звіт сяде в середнє ЦІЛКОМ — інакше EMA повзла б від нуля
    //    кілька звітів і пропустила б ранній стан каналу
    if (!t->seeded) {
        t->loss_avg   = loss;
        t->jitter_avg = jitter;
        t->seeded     = 1;
    }

    // 1) згладжуємо обидва датчики — гасимо одиничні сплески
    t->loss_avg   = ema_u16(t->loss_avg, loss, t->alpha_pct);
    // джитер 32-бітний — згладимо окремо тим самим правилом
    {
        int64_t dj = (int64_t)jitter - (int64_t)t->jitter_avg;
        t->jitter_avg = (uint32_t)((int64_t)t->jitter_avg
                                   + dj * t->alpha_pct / 100);
    }

    // 2) РАННЄ ПОПЕРЕДЖЕННЯ за джитером: він росте швидко, а втрат ще нема —
    //    канал ось-ось захлинеться. Не піднімаємось, навіть якщо втрати малі.
    int jitter_rising = ((int64_t)jitter > (int64_t)t->jitter_avg * 3 / 2);

    if (jitter_rising && t->loss_avg < t->base.loss_up_permille) {
        // притримуємо ріст: пропускаємо крок угору, лишаємо бітрейт як є
        return t->base.rate;
    }

    // 3) рішення — на ЗГЛАДЖЕНИХ втратах, не на сирих.
    //    переводимо ‰ (0..1000) назад у формат RR (0..255) і затискаємо стелею:
    uint32_t f255 = ((uint32_t)t->loss_avg << 8) / 1000u;   // ‰ → 0..256
    if (f255 > 255u) f255 = 255u;                            // 100% не має дати 0!
    return abr_on_report(&t->base, (uint8_t)f255);
}
