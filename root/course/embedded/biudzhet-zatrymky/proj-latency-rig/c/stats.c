#include "stats.h"

void stats_init(stats_t *s)
{
    s->count    = 0u;
    s->timeouts = 0u;
    s->sorted   = false;
    for (uint16_t i = 0u; i < STATS_MAX_SAMPLES; ++i) {
        s->samples[i] = 0u;
    }
}

bool stats_add(stats_t *s, uint32_t latency_us)
{
    if (s->count >= STATS_MAX_SAMPLES) {
        return false;
    }
    s->samples[s->count++] = latency_us;
    s->sorted = false;
    return true;
}

void stats_add_timeout(stats_t *s)
{
    if (s->timeouts < UINT16_MAX) {
        s->timeouts++;
    }
}

// Сортування вставками: на 256 зразках воно швидше за будь-яку рекурсію,
// не потребує ні стека, ні тимчасового буфера — а другого буфера на 1 КБ
// у мікроконтролера просто немає.
static void sort_in_place(uint32_t *arr, uint16_t n)
{
    for (uint16_t i = 1u; i < n; ++i) {
        const uint32_t key = arr[i];
        uint16_t j = i;
        while (j > 0u && arr[j - 1u] > key) {
            arr[j] = arr[j - 1u];
            --j;
        }
        arr[j] = key;
    }
}

// Перцентиль за методом найближчого рангу: індекс = ceil(p/100 * n) - 1.
// Наївне (n * p) / 100 зсуває оцінку вниз — на 256 зразках P99 показав би
// 253-й елемент замість 254-го, тобто саме той сплеск, заради якого міряють.
static uint32_t percentile(const uint32_t *sorted, uint16_t n, uint16_t p)
{
    const uint32_t rank = ((uint32_t)n * p + 99u) / 100u;
    uint32_t index = (rank == 0u) ? 0u : (rank - 1u);
    if (index >= n) {
        index = (uint32_t)n - 1u;
    }
    return sorted[index];
}

bool stats_summarize(stats_t *s, stats_summary_t *out)
{
    out->count    = s->count;
    out->timeouts = s->timeouts;

    if (s->count == 0u) {
        out->min_us = out->max_us = out->mean_us = 0u;
        out->p50_us = out->p95_us = out->p99_us = 0u;
        out->jitter_us = 0u;
        return false;
    }

    if (!s->sorted) {
        sort_in_place(s->samples, s->count);
        s->sorted = true;
    }

    const uint32_t *v = s->samples;
    const uint16_t  n = s->count;

    out->min_us = v[0];
    out->max_us = v[n - 1u];

    // Сума 256 інтервалів по чверті секунди не влазить у 32 біти — рахуємо в 64.
    uint64_t sum = 0u;
    for (uint16_t i = 0u; i < n; ++i) {
        sum += v[i];
    }
    out->mean_us = (uint32_t)(sum / n);

    out->p50_us = percentile(v, n, 50u);
    out->p95_us = percentile(v, n, 95u);
    out->p99_us = percentile(v, n, 99u);

    // Джитер міряємо як середнє відхилення від МЕДІАНИ, а не від середнього:
    // одна ретрансмісія на межі дальності тягне середнє за собою, і джитер
    // роздувся б від того самого викиду, який медіана вже відсіяла.
    uint64_t deviation = 0u;
    for (uint16_t i = 0u; i < n; ++i) {
        deviation += (v[i] > out->p50_us) ? (v[i] - out->p50_us) : (out->p50_us - v[i]);
    }
    out->jitter_us = (uint32_t)(deviation / n);

    return true;
}
