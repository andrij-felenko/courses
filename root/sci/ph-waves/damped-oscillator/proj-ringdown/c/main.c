#include <math.h>
#include <stdint.h>

#define FOUR_PI2  39.4784176f          /* 4·π² */

typedef struct {
    float    fs, floor, prev;
    int      rising, peaks;
    float    a_first, a_last;          /* висоти першої й останньої вершини */
    uint32_t n_first, n_last, idx;     /* їхні номери відліків */
} Ring;

void ring_init(Ring *r, float fs, float noise_floor) {
    r->fs = fs; r->floor = 6.0f * noise_floor;    /* довіра лише над шумом */
    r->prev = 0.0f; r->rising = 0; r->peaks = 0;
    r->a_first = r->a_last = 0.0f;
    r->n_first = r->n_last = 0; r->idx = 0;
}

/* Годуємо по одному відліку; повертає 1, коли щойно прийнято нову вершину.
   Детектор варто «зводити» після удару, коли сигнал уже піднявся над floor. */
int ring_push(Ring *r, float x) {
    int got = 0;
    if (r->rising && x < r->prev && r->prev > r->floor) {
        if (r->peaks == 0) { r->a_first = r->prev; r->n_first = r->idx - 1; }
        r->a_last = r->prev; r->n_last = r->idx - 1;
        r->peaks++; got = 1;
    }
    r->rising = (x > r->prev);
    r->prev = x; r->idx++;
    return got;
}

/* Коли вершин зібралося досить — витягуємо ζ, Q, f_d. 0, якщо замало. */
int ring_result(const Ring *r, float *zeta, float *Q, float *f_d) {
    if (r->peaks < 3) return 0;
    int   cycles = r->peaks - 1;
    float delta  = logf(r->a_first / r->a_last) / (float)cycles;
    float z      = delta / sqrtf(FOUR_PI2 + delta * delta);
    float Td     = (float)(r->n_last - r->n_first) / (r->fs * (float)cycles);
    *zeta = z;
    *Q    = 1.0f / (2.0f * z);
    *f_d  = 1.0f / Td;
    return 1;
}
