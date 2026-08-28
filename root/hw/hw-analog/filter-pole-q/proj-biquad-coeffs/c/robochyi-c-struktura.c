#include <math.h>
#include <stdint.h>
#include <stddef.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Одна біквад-ланка (Direct Form I): 5 коефіцієнтів + 4 значення стану.
typedef struct {
    float b0, b1, b2;     // чисельник (нулі — що фільтр гасить)
    float a1, a2;         // знаменник (полюси — пара ω₀, Q); a0 нормовано до 1
    float x1, x2;         // два минулі входи  x[n−1], x[n−2]
    float y1, y2;         // два минулі виходи y[n−1], y[n−2]
} biquad;
