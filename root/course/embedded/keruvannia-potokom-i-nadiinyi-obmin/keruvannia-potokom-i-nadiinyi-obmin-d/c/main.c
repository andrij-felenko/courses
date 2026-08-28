#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t rate_bytes_per_sec; // Середня дозволена швидкість
    uint32_t capacity_tokens;    // Максимальний сплеск
    uint32_t current_tokens;     // Поточний залишок токенів
    uint32_t last_update_ms;     // Час останнього оновлення за системним таймером
} TokenBucket;

void token_bucket_init(TokenBucket *tb, uint32_t rate, uint32_t capacity, uint32_t now_ms) {
    tb->rate_bytes_per_sec = rate;
    tb->capacity_tokens = capacity;
    tb->current_tokens = capacity;
    tb->last_update_ms = now_ms;
}

// Оновлення кількості токенів на основі дельти часу
static void token_bucket_update(TokenBucket *tb, uint32_t now_ms) {
    uint32_t delta_ms = now_ms - tb->last_update_ms;
    if (delta_ms > 0) {
        // Додаємо токени: (delta_ms * rate) / 1000
        uint32_t new_tokens = (uint32_t)(((uint64_t)delta_ms * tb->rate_bytes_per_sec) / 1000ULL);
        if (new_tokens > 0) {
            uint32_t updated = tb->current_tokens + new_tokens;
            tb->current_tokens = (updated > tb->capacity_tokens) ? tb->capacity_tokens : updated;
            tb->last_update_ms = now_ms;
        }
    }
}

// Перевірка можливості відправки пакета розміром size_bytes
bool token_bucket_consume(TokenBucket *tb, uint32_t size_bytes, uint32_t now_ms) {
    token_bucket_update(tb, now_ms);
    if (tb->current_tokens >= size_bytes) {
        tb->current_tokens -= size_bytes;
        return true; // Дозвіл на відправку
    }
    return false; // Заборона: перевищено ліміт темпу
}
