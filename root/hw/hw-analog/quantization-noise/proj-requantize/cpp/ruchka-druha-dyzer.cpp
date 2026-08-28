#include <stdint.h>

// Дешевий швидкий генератор псевдовипадкових (xorshift32).
// Тримає власний стан; на кожен виклик — новий 32-розрядний кидок.
static uint32_t rng_state = 0x1234567u;

static inline uint32_t xorshift32(void)
{
    uint32_t s = rng_state;
    s ^= s << 13;
    s ^= s >> 17;
    s ^= s << 5;
    rng_state = s;
    return s;
}

// TPDF-дизер розмахом ±q (тобто повний розмах 2q) для скорочення на S розрядів.
// q = 1<<S — крок нової сітки в одиницях старого слова.
static inline int32_t tpdf_dither(int S)
{
    uint32_t q = 1u << S;
    // два незалежні рівномірні на [0, q) — їхня сума трикутна на [0, 2q)
    int32_t r1 = (int32_t)(xorshift32() % q);
    int32_t r2 = (int32_t)(xorshift32() % q);
    // зсунути так, щоб центр був у нулі: розмах стає [−q, +q)
    return r1 + r2 - (int32_t)q;
}

int16_t requantize_dither(int32_t x24, int S)
{
    int32_t d = tpdf_dither(S);                 // ±q, трикутний
    int32_t half = 1 << (S - 1);                // пів-кроку для округлення
    return (int16_t)((x24 + d + half) >> S);    // сигнал + дизер + ½q, тоді зсув
}
