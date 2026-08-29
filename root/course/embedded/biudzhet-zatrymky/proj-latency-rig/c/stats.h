// Накопичувач вибірки й порядкова статистика. Уся пам'ять статична: на стенді
// немає ні купи, ні файлової системи, а вибірка відома наперед — 256 зразків.
#ifndef STATS_H
#define STATS_H

#include <stdbool.h>
#include <stdint.h>

#define STATS_MAX_SAMPLES 256u

typedef struct {
    uint32_t samples[STATS_MAX_SAMPLES];
    uint16_t count;    // скільки успішних вимірів лежить у samples
    uint16_t timeouts; // скільки випробувань завершилося втратою кадру
    bool     sorted;   // samples уже впорядковано на місці
} stats_t;

typedef struct {
    uint16_t count;
    uint16_t timeouts;
    uint32_t min_us;
    uint32_t max_us;
    uint32_t mean_us;
    uint32_t p50_us;
    uint32_t p95_us;
    uint32_t p99_us;
    uint32_t jitter_us; // середнє абсолютне відхилення від медіани
} stats_summary_t;

void stats_init(stats_t *s);

// Зараховує успішний вимір. false — вибірка заповнена, зразок відкинуто.
bool stats_add(stats_t *s, uint32_t latency_us);

void stats_add_timeout(stats_t *s);

// Рахує зведення. false — жодного успішного виміру, рахувати нічого.
// Сортує вибірку на місці, тому після виклику порядок зразків утрачено.
bool stats_summarize(stats_t *s, stats_summary_t *out);

#endif // STATS_H
