// Простенький генератор псевдовипадкових чисел (xorshift32) — швидкий, без ділень.
static uint32_t rng_state = 0x1234567u;
static inline int32_t dither_lsb(void) {
    uint32_t r = rng_state;
    r ^= r << 13;  r ^= r >> 17;  r ^= r << 5;
    rng_state = r;
    // ±1 молодший біт: беремо два біти й центруємо в діапазон [-1, +1]
    return (int32_t)(r & 3u) - 1;      // {-1, 0, 1, 2} → зсунуте, вистачить для розбиття циклу
}

int32_t biquad_q31_dither_step(biquad_q31_ps_t *s, int32_t x) {
    int64_t acc  = (int64_t)s->b0 * x;
    acc         += (int64_t)s->b1 * s->x1;
    acc         += (int64_t)s->b2 * s->x2;
    acc         -= (int64_t)s->a1 * s->y1;
    acc         -= (int64_t)s->a2 * s->y2;

    int sh = 31 - s->postShift;
    acc = (acc + (1LL << (sh - 1))) >> sh;
    acc += dither_lsb();               // ← підмішуємо ±1 LSB перед звуженням

    int32_t y = sat32(acc);
    s->x2 = s->x1;  s->x1 = x;
    s->y2 = s->y1;  s->y1 = y;
    return y;
}
