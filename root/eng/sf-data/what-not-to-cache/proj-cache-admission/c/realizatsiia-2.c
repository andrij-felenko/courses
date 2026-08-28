#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define BLOOM_BITS 65536
#define BLOOM_WORDS (BLOOM_BITS / 64)
#define BLOOM_MASK (BLOOM_BITS - 1)
#define BLOOM_ROTATION_THRESHOLD 8000

typedef struct {
    uint64_t active[BLOOM_WORDS];
    uint64_t previous[BLOOM_WORDS];
    uint32_t insert_count;
} SegmentedBloomFilter;

void bloom_init(SegmentedBloomFilter *bf) {
    memset(bf->active, 0, sizeof(bf->active));
    memset(bf->previous, 0, sizeof(bf->previous));
    bf->insert_count = 0;
}

static inline void bloom_add_bit(uint64_t *table, uint32_t bit_idx) {
    table[bit_idx / 64] |= (1ULL << (bit_idx % 64));
}

static inline bool bloom_test_bit(const uint64_t *table, uint32_t bit_idx) {
    return (table[bit_idx / 64] & (1ULL << (bit_idx % 64))) != 0;
}

/* Обчислення двох незалежних бітових індексів через Murmur-подібний хеш */
static void bloom_get_indices(const char *key, size_t len, uint32_t *idx1, uint32_t *idx2) {
    uint64_t h1 = 0x100000001b3ULL ^ (len * 0x517cc1b727220a95ULL);
    uint64_t h2 = 0xcbf29ce484222325ULL ^ len;
    for (size_t i = 0; i < len; ++i) {
        h1 = (h1 ^ (uint8_t)key[i]) * 0x5bd1e9955bd1e995ULL;
        h2 = (h2 ^ (uint8_t)key[i]) * 0x9e3779b97f4a7c15ULL;
    }
    *idx1 = (uint32_t)(h1 & BLOOM_MASK);
    *idx2 = (uint32_t)(h2 & BLOOM_MASK);
}

/* Перевірка допуску: повертає true, якщо ключ бачили раніше */
bool bloom_check_and_record(SegmentedBloomFilter *bf, const char *key, size_t len) {
    uint32_t idx1, idx2;
    bloom_get_indices(key, len, &idx1, &idx2);

    bool in_active = bloom_test_bit(bf->active, idx1) && bloom_test_bit(bf->active, idx2);
    bool in_prev   = bloom_test_bit(bf->previous, idx1) && bloom_test_bit(bf->previous, idx2);

    // Додаємо в поточний активний фільтр
    bloom_add_bit(bf->active, idx1);
    bloom_add_bit(bf->active, idx2);
    bf->insert_count++;

    // Ротація фільтрів при досягненні ліміту
    if (bf->insert_count >= BLOOM_ROTATION_THRESHOLD) {
        memcpy(bf->previous, bf->active, sizeof(bf->active));
        memset(bf->active, 0, sizeof(bf->active));
        bf->insert_count = 0;
    }

    return in_active || in_prev;
}
