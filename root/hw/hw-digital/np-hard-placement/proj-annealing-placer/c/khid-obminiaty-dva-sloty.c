/* xorshift64* Марсальї.
   rand() тут не годиться: його кличуть сотні мільйонів разів, а він
   у багатьох бібліотеках короткоперіодний і лізе в блокування. */
static uint64_t rng = 0x853c49e6748fea9bULL;

static inline uint32_t rnd_u32(void)
{
    uint64_t x = rng;
    x ^= x >> 12;
    x ^= x << 25;
    x ^= x >> 27;
    rng = x;
    return (uint32_t)((x * 0x2545F4914F6CDD1DULL) >> 32);
}

/* Рівномірно 0 .. n−1, без ділення (множення зі зсувом, спосіб Леміра).
   Дає крихітний перекіс на краю діапазону — для відпалу байдужий. */
static inline int rnd_below(int n)
{
    return (int)(((uint64_t)rnd_u32() * (uint64_t)n) >> 32);
}

/* Рівномірно [0, 1). */
static inline double rnd_unit(void)
{
    return rnd_u32() * (1.0 / 4294967296.0);
}
