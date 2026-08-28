#include <stdint.h>

// Один біквад у Q31, пряма форма I.
// Коефіцієнти вже в Q31 (дріб × 2^31), a1,a2 — УЖЕ зі знаком «−» у формулі.
typedef struct {
    int32_t b0, b1, b2;     // пряма гілка (входи)
    int32_t a1, a2;         // зворотна гілка (виходи)
    int32_t x1, x2;         // x[n-1], x[n-2]  — попередні входи
    int32_t y1, y2;         // y[n-1], y[n-2]  — попередні виходи
} biquad_q31_t;

// затиск 64-бітного значення у діапазон int32_t: НАСИЧЕННЯ, не загортання
static inline int32_t sat32(int64_t v) {
    if (v >  INT32_MAX) return INT32_MAX;
    if (v <  INT32_MIN) return INT32_MIN;
    return (int32_t)v;
}

int32_t biquad_q31_step(biquad_q31_t *s, int32_t x) {
    // acc у форматі Q62: множення Q31×Q31 без округлення, копимо в 64 біти
    int64_t acc  = (int64_t)s->b0 * x;
    acc         += (int64_t)s->b1 * s->x1;
    acc         += (int64_t)s->b2 * s->x2;
    acc         -= (int64_t)s->a1 * s->y1;
    acc         -= (int64_t)s->a2 * s->y2;

    // Q62 → Q31: зсув на 31 з округленням (додаємо половину молодшого розряду)
    acc = (acc + (1LL << 30)) >> 31;

    int32_t y = sat32(acc);          // звужуємо в 32 біти з насиченням

    // зсуваємо лінії затримки на один такт
    s->x2 = s->x1;  s->x1 = x;
    s->y2 = s->y1;  s->y1 = y;
    return y;
}
