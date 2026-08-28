#include <stddef.h>

// Один біквад, пряма форма I. Стан — два минулі входи й два минулі виходи.
typedef struct {
    float b0, b1, b2;     // коефіцієнти прямої гілки (входи)
    float a1, a2;         // коефіцієнти зворотної гілки (виходи); у формулі віднімаються
    float x1, x2;         // x[n-1], x[n-2]
    float y1, y2;         // y[n-1], y[n-2]
} biquad_t;

float biquad_step(biquad_t *s, float x) {
    float y = s->b0 * x  + s->b1 * s->x1 + s->b2 * s->x2
                         - s->a1 * s->y1 - s->a2 * s->y2;   // 5 множень
    // зсуваємо лінії затримки на один такт
    s->x2 = s->x1;  s->x1 = x;
    s->y2 = s->y1;  s->y1 = y;
    return y;
}
