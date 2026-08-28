// ── Дизеринг: розбити холості тони крихітним шумом на вході ───────────────
// Дешевий генератор псевдовипадкових чисел (xorshift) — швидкий, без множень.
static uint32_t rng_state = 0x1234ABCDu;

static inline uint32_t rng_next(void)
{
    uint32_t x = rng_state;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;   // три зсуви — і готово
    return (rng_state = x);
}

// Додати дизер до рівня ПЕРЕД модулятором. Амплітуда дизера крихітна:
// одиниці молодшого розряду, не більше — інакше задавимо корисний сигнал.
static inline uint8_t add_dither(uint8_t level)
{
    int32_t d = (int32_t)(rng_next() & 0x3u) - 1;   // шум у межах -1..+2 LSB
    int32_t v = (int32_t)level + d;
    if (v < 0)   v = 0;                              // не випасти за межі шкали
    if (v > 255) v = 255;
    return (uint8_t)v;
}
