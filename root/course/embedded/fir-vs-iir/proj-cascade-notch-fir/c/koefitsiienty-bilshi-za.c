typedef struct {
    int32_t b0, b1, b2, a1, a2;   // коефіцієнти, ПОДІЛЕНІ на 2^postShift → влазять у [-1,1)
    int32_t x1, x2, y1, y2;
    int      postShift;           // на стільки біт домножити суму назад
} biquad_q31_ps_t;

int32_t biquad_q31_ps_step(biquad_q31_ps_t *s, int32_t x) {
    int64_t acc  = (int64_t)s->b0 * x;
    acc         += (int64_t)s->b1 * s->x1;
    acc         += (int64_t)s->b2 * s->x2;
    acc         -= (int64_t)s->a1 * s->y1;
    acc         -= (int64_t)s->a2 * s->y2;

    // Q62 → Q31, а тоді домножити на 2^postShift (повертаємо поділені коефіцієнти):
    // разом це зсув праворуч на (31 - postShift).
    int sh = 31 - s->postShift;
    acc = (acc + (1LL << (sh - 1))) >> sh;

    int32_t y = sat32(acc);
    s->x2 = s->x1;  s->x1 = x;
    s->y2 = s->y1;  s->y1 = y;
    return y;
}
