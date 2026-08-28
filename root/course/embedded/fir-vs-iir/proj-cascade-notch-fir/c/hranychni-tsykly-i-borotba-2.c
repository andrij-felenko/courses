typedef struct {
    biquad_q31_ps_t bq;
    int64_t err;              // збережений «хвіст» — відкинуті молодші біти
} biquad_ef_t;

int32_t biquad_q31_ef_step(biquad_ef_t *s, int32_t x) {
    biquad_q31_ps_t *b = &s->bq;
    int64_t acc  = (int64_t)b->b0 * x;
    acc         += (int64_t)b->b1 * b->x1;
    acc         += (int64_t)b->b2 * b->x2;
    acc         -= (int64_t)b->a1 * b->y1;
    acc         -= (int64_t)b->a2 * b->y2;

    int sh = 31 - b->postShift;
    acc += s->err;                       // ← повертаємо збережений хвіст минулого кроку
    int64_t rounded = (acc + (1LL << (sh - 1))) >> sh;
    s->err = acc - (rounded << sh);      // ← запам'ятовуємо новий хвіст (що відкинули)

    int32_t y = sat32(rounded);
    b->x2 = b->x1;  b->x1 = x;
    b->y2 = b->y1;  b->y1 = y;
    return y;
}
