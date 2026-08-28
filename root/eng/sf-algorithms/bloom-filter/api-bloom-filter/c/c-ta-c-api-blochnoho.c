#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef struct __attribute__((aligned(64))) {
    uint32_t buckets[16]; /* 16 слів * 32 біти = 512 бітів = 64 байти */
} bloom_block_t;

typedef struct {
    bloom_block_t *blocks; /* Вирівняний масив 64-байтових кеш-блоків */
    size_t num_blocks;     /* Загальна кількість блоків */
    size_t k;              /* Кількість бітів у блоці (зазвичай k = 8) */
} blocked_bloom_filter_t;

/**
 * Ініціалізує блочний фільтр Блума з вирівнюванням пам'яті aligned_alloc.
 */
bool blocked_bloom_init(blocked_bloom_filter_t *bf, size_t num_blocks, size_t k);

/**
 * Додає елемент у блочний фільтр за двома 64-бітними хешами.
 */
void blocked_bloom_add(blocked_bloom_filter_t *bf, uint64_t h1, uint64_t h2);

/**
 * Здійснює перевірку ключа з гарантією строго 1 промаху кешу L3.
 */
bool blocked_bloom_contains(const blocked_bloom_filter_t *bf, uint64_t h1, uint64_t h2);

/**
 * Звільняє пам'ять вирівняного вектору блоків.
 */
void blocked_bloom_free(blocked_bloom_filter_t *bf);
