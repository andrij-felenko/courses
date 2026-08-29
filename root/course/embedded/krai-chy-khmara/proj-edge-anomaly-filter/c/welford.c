#include "welford.h"

#include <math.h>

void welford_reset(welford_t *s)
{
    s->count = 0;
    s->mean  = 0.0f;
    s->m2    = 0.0f;
}

void welford_update(welford_t *s, float x)
{
    if (!isfinite(x)) {
        return;
    }

    /* Насичення лічильника. За 1.4 року на 100 Гц uint32 переповниться,
       і count упав би в нуль — ділення на нуль просто в оновленні середнього.
       Насичений лічильник заморожує адаптацію, але не ламає числа;
       від дрейфу робочої точки все одно рятує періодичний reset. */
    if (s->count == UINT32_MAX) {
        return;
    }
    s->count++;

    const float delta = x - s->mean;
    s->mean += delta / (float)s->count;
    const float delta2 = x - s->mean;   /* уже з НОВИМ середнім — у цьому вся суть */
    s->m2 += delta * delta2;
}

uint32_t welford_count(const welford_t *s)
{
    return s->count;
}

float welford_mean(const welford_t *s)
{
    return s->mean;
}

float welford_variance(const welford_t *s)
{
    if (s->count < 2) {
        return 0.0f;
    }
    /* m2 математично невід'ємна, але при екстремальних даних округлення
       здатне зіштовхнути її трохи нижче нуля — sqrtf від'ємного дав би NaN. */
    const float var = s->m2 / (float)(s->count - 1u);
    return (var > 0.0f) ? var : 0.0f;
}

float welford_stddev(const welford_t *s)
{
    return sqrtf(welford_variance(s));
}

float welford_zscore(const welford_t *s, float x)
{
    const float sigma = welford_stddev(s);
    if (sigma < 1e-6f || !isfinite(x)) {
        return 0.0f;
    }
    return fabsf(x - s->mean) / sigma;
}
