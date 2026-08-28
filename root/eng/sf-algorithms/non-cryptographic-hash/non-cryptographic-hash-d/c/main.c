#include <stdint.h>
#include <stddef.h>
#include <string.h>

static const uint64_t C1 = 0x87c37b91114253d5ULL;
static const uint64_t C2 = 0x4cf5ad432745937fULL;

static inline uint64_t load64(const uint8_t *p) {
    uint64_t v;
    memcpy(&v, p, sizeof(v)); /* Блискавичне читання без UB */
    return v;
}

static inline uint64_t rotl64(uint64_t x, int8_t r) {
    return (x << r) | (x >> (64 - r));
}

uint64_t simple_fast_hash(const void *key, size_t len, uint64_t seed) {
    const uint8_t *data = (const uint8_t *)key;
    const size_t nblocks = len / 8;
    uint64_t h1 = seed ^ (len * C1);

    for (size_t i = 0; i < nblocks; i++) {
        uint64_t k1 = load64(data + i * 8);
        k1 *= C1;
        k1 = rotl64(k1, 31);
        k1 *= C2;

        h1 ^= k1;
        h1 = rotl64(h1, 27);
        h1 = h1 * 5 + 0x52dce729;
    }

    /* Обробка хвоста та фіналізатор */
    h1 ^= len;
    h1 ^= h1 >> 33;
    h1 *= 0xff51afd7565a1a5dULL;
    h1 ^= h1 >> 33;
    return h1;
}
