#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>

typedef struct {
    uint64_t table[8][256];
    uint64_t mask;
} tabulation_hasher_t;

void tabulation_hasher_init(tabulation_hasher_t *h, uint32_t M, uint64_t (*rng_func)(void)) {
    h->mask = (1ULL << M) - 1;
    for (int i = 0; i < 8; i++) {
        for (int j = 0; j < 256; j++) {
            h->table[i][j] = rng_func();
        }
    }
}

uint64_t tabulation_hasher_eval(const tabulation_hasher_t *h, uint64_t x) {
    uint64_t hash = 0;
    hash ^= h->table[0][(x >>  0) & 0xFF];
    hash ^= h->table[1][(x >>  8) & 0xFF];
    hash ^= h->table[2][(x >> 16) & 0xFF];
    hash ^= h->table[3][(x >> 24) & 0xFF];
    hash ^= h->table[4][(x >> 32) & 0xFF];
    hash ^= h->table[5][(x >> 40) & 0xFF];
    hash ^= h->table[6][(x >> 48) & 0xFF];
    hash ^= h->table[7][(x >> 56) & 0xFF];
    return hash & h->mask;
}
