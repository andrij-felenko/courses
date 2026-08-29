#ifndef EDGE_WELFORD_H
#define EDGE_WELFORD_H

#include <stdint.h>

/*
 * Потокова статистика за алгоритмом Велфорда (B. P. Welford, 1962).
 *
 * Стан — три поля, оновлення — сталий час, купа не потрібна взагалі.
 * Наївне E[X^2] - (E[X])^2 на float тут дало б катастрофічне скасування
 * розрядів: для 230.0 В із шумом 0.1 В обидва доданки близькі до 52900,
 * а їхня різниця — 0.01. Мантиси float (24 біти) на це не вистачає.
 */
typedef struct {
    uint32_t count;
    float    mean;
    float    m2;   /* сума квадратів відхилень від поточного середнього */
} welford_t;

void welford_reset(welford_t *s);

/* Не-скінченні вибірки ігноруються: одна NaN назавжди отруїла б mean і m2. */
void welford_update(welford_t *s, float x);

uint32_t welford_count(const welford_t *s);
float    welford_mean(const welford_t *s);
float    welford_variance(const welford_t *s);
float    welford_stddev(const welford_t *s);

/* |x - mean| / sigma. При sigma < 1e-6 повертає 0: сигнал-константа
   (обрив давача, коротке на шину живлення) не повинен давати нескінченність. */
float welford_zscore(const welford_t *s, float x);

#endif /* EDGE_WELFORD_H */
