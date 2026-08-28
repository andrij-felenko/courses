// DC-blocker: y[n] = x[n] − x[n−1] + α·y[n−1].
// α близьке до 1 (тут 0.995) — зрізає лише найповільніший зсув, звук лишає.
// Стан у 32-бітному цілому з фіксованою комою, щоб не тягти float у переривання.
typedef struct { int32_t x_prev, y_prev; } dcblock_t;

int32_t dcblock(dcblock_t *s, int32_t x) {
    // α = 0.995 у форматі Q15: 0.995 · 32768 ≈ 32604
    int32_t y = x - s->x_prev + (int32_t)(((int64_t)32604 * s->y_prev) >> 15);
    s->x_prev = x;
    s->y_prev = y;
    return y;
}
