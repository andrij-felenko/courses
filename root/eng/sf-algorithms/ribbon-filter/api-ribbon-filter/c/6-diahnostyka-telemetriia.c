#include <stddef.h>
#include <stdint.h>

typedef struct {
    size_t num_keys;              /* Кількість вхідних ключів */
    size_t num_slots;             /* Загальна кількість слотів */
    size_t memory_bytes;          /* Фактичний обсяг виділеної пам'яті */
    double bits_per_key;          /* Питома кількість бітів на один ключ */
    double theoretical_fpr;       /* Теоретична ймовірність помилки 2^(-r) */
    uint32_t retries_count;       /* Кількість спроб побудови зі зміною seed */
    double build_time_ms;         /* Час побудови у мілісекундах */
} RibbonStats;

RibbonStatus ribbon_get_stats(const RibbonFilter *filter, RibbonStats *out_stats);
