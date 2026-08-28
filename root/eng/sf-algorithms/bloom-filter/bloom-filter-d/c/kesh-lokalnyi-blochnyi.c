#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t buckets[16]; /* 16 * 32 біти = 512 бітів = 64 байти */
} __attribute__((aligned(64))) cache_block_t;

/* Перевірка елемента у блочному фільтрі Блума */
bool blocked_bloom_check(const cache_block_t *blocks, size_t num_blocks, uint64_t h1, uint64_t h2) {
    size_t block_idx = h1 % num_blocks;
    const cache_block_t *block = &blocks[block_idx];

    /* Всі k бітів перевіряються всередині знайденого 64-байтового блоку */
    for (size_t i = 0; i < 8; i++) {
        uint32_t bit_idx = (uint32_t)((h2 + i * 0x9e3779b9u) & 511);
        uint32_t bucket = block->buckets[bit_idx >> 5];
        if ((bucket & (1u << (bit_idx & 31))) == 0) {
            return false; /* 0 промахів кешу після завантаження блоку */
        }
    }
    return true;
}
