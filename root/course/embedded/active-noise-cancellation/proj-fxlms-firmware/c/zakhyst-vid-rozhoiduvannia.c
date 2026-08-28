// детектор розбіжності: стежимо за повільним зростанням енергії помилки
static int32_t err_pow_ema = 0;       // ковзне середнє e², Q-масштаб умовний
static int     diverge_cnt = 0;

static void watchdog(q15_t err)
{
    int32_t e2 = ((int32_t)err * (int32_t)err) >> Q;     // миттєва e², Q15
    // EMA: err_pow += (e² − err_pow) / 64
    err_pow_ema += (e2 - err_pow_ema) >> 6;

    if (err_pow_ema > DIVERGE_LEVEL) {
        if (++diverge_cnt > DIVERGE_HOLD) {              // тримається довго → це розгін
            for (int i = 0; i < N; ++i) wq[i] = 0;      // АВАРІЙНИЙ скид фільтра
            diverge_cnt = 0;
            request_reidentify();                        // попросити перевиміряти S
        }
    } else {
        diverge_cnt = 0;                                 // помилка спала — все гаразд
    }
}
