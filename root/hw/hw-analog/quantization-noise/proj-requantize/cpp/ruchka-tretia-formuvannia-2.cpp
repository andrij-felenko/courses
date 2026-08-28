#include <stdint.h>

static uint32_t rng_state = 0x1234567u;
static int32_t  ns_err    = 0;

static inline uint32_t xorshift32(void)
{
    uint32_t s = rng_state;
    s ^= s << 13; s ^= s >> 17; s ^= s << 5;
    rng_state = s;
    return s;
}

// Повний перекодувач: округлення + TPDF-дизер + формування шуму 1-го порядку.
int16_t requantize_full(int32_t x24, int S)
{
    uint32_t q    = 1u << S;
    int32_t  half = 1 << (S - 1);

    // TPDF-дизер розмахом ±q (сума двох рівномірних)
    int32_t d = (int32_t)(xorshift32() % q)
              + (int32_t)(xorshift32() % q) - (int32_t)q;

    // формування: додаємо і дизер, і накопичену похибку
    int32_t u = x24 + d + ns_err;
    int16_t y = (int16_t)((u + half) >> S);

    // похибку рахуємо БЕЗ дизера — переносити треба лише похибку округлення,
    // не наш власний доданий шум (інакше формувач боровся б із дизером)
    int32_t u_clean = x24 + ns_err;
    ns_err = u_clean - ((int32_t)y << S);
    return y;
}
