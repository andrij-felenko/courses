#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    uint32_t width;
    uint32_t depth;
    uint32_t *table;
    uint64_t *seeds;
} cm_sketch_mini_t;

/* Простий хеш-міксер Murmur3 для демонстрації */
static inline uint32_t cm_hash(const void *data, size_t len, uint64_t seed) {
    const uint8_t *bytes = (const uint8_t *)data;
    uint32_t h = (uint32_t)seed ^ (uint32_t)len;
    for (size_t i = 0; i < len; ++i) {
        h ^= bytes[i];
        h *= 0x5bd1e995;
        h ^= h >> 15;
    }
    return h;
}

void cm_mini_add(cm_sketch_mini_t *s, const void *key, size_t len, uint32_t count) {
    for (uint32_t r = 0; r < s->depth; ++r) {
        uint32_t col = cm_hash(key, len, s->seeds[r]) % s->width;
        s->table[r * s->width + col] += count;
    }
}

uint32_t cm_mini_query(const cm_sketch_mini_t *s, const void *key, size_t len) {
    uint32_t res = UINT32_MAX;
    for (uint32_t r = 0; r < s->depth; ++r) {
        uint32_t col = cm_hash(key, len, s->seeds[r]) % s->width;
        uint32_t val = s->table[r * s->width + col];
        if (val < res) res = val;
    }
    return res;
}
