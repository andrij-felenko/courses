// Фільтр дедуплікації на базі ковзного бітового масиву (C)
#include <stdint.h>
#include <stdbool.h>

#define WINDOW_SIZE 64

typedef struct {
    uint64_t max_seq_seen;
    uint64_t bitmask; // біт 0 відповідає max_seq_seen - 1
} SlidingWindowDeduplicator;

void dedup_init(SlidingWindowDeduplicator *d) {
    d->max_seq_seen = 0;
    d->bitmask = 0;
}

// Повертає true, якщо пакет новий і валідний; false, якщо це дублікат чи застарілий
bool dedup_is_valid(SlidingWindowDeduplicator *d, uint64_t seq) {
    if (seq == 0) return false;

    // Перший отриманий пакет
    if (d->max_seq_seen == 0) {
        d->max_seq_seen = seq;
        d->bitmask = 0;
        return true;
    }

    // Пакет новіший за всі бачені раніше
    if (seq > d->max_seq_seen) {
        uint64_t diff = seq - d->max_seq_seen;
        if (diff < WINDOW_SIZE) {
            d->bitmask = (d->bitmask << diff) | (1ULL << (diff - 1));
        } else {
            d->bitmask = 0; // пропустили великий інтервал
        }
        d->max_seq_seen = seq;
        return true;
    }

    // Пакет зі старішим seq_id
    uint64_t diff = d->max_seq_seen - seq;
    if (diff == 0 || diff > WINDOW_SIZE) {
        return false; // Дублікат або випав за межі вікна
    }

    uint64_t mask = 1ULL << (diff - 1);
    if (d->bitmask & mask) {
        return false; // Вже був отриманий раніше (дублікат QoS 1)
    }

    // Запізнілий пакет, який прийшов вперше
    d->bitmask |= mask;
    return true;
}
