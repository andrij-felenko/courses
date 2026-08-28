#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#define CACHE_LINE_BYTES 64
#define BITS_PER_BLOCK   (CACHE_LINE_BYTES * 8) // 512 бітів
#define WORDS_PER_BLOCK  (CACHE_LINE_BYTES / sizeof(uint64_t)) // 8 слів по 64 біти

// Блок розміром рівно в одну кеш-лінію (64 байти)
typedef struct {
    uint64_t words[WORDS_PER_BLOCK];
} cache_block_t;

typedef struct {
    cache_block_t *blocks;
    size_t num_blocks;
    uint32_t k_hashes;
} blocked_bloom_t;

// 64-бітний швидкий некриптографічний геш MurmurHash3 / SplitMix64
static inline uint64_t hash_step(uint64_t x) {
    x ^= x >> 30;
    x *= 0xbf58476d1ce4e5b9ULL;
    x ^= x >> 27;
    x *= 0x94d049bb133111ebULL;
    x ^= x >> 31;
    return x;
}

// Ініціалізація блочного фільтра Блума
blocked_bloom_t* blocked_bloom_create(size_t num_elements, double fp_rate) {
    if (num_elements == 0 || fp_rate <= 0.0 || fp_rate >= 1.0) return NULL;

    // Розрахунок необхідної кількості бітів: m = -n * ln(p) / (ln(2))^2
    // Для блочного фільтра додаємо невеликий запас (+15%) на дисперсію завантаження блоків
    size_t total_bits = (size_t)(-1.65 * (double)num_elements * (fp_rate > 0.01 ? -4.6 : -6.9));
    size_t num_blocks = (total_bits + BITS_PER_BLOCK - 1) / BITS_PER_BLOCK;
    if (num_blocks == 0) num_blocks = 1;

    blocked_bloom_t *filter = (blocked_bloom_t*)malloc(sizeof(blocked_bloom_t));
    if (!filter) return NULL;

    // Виділення пам'яті з апаратним вирівнюванням по 64 байти
    void *raw_ptr = NULL;
    if (posix_memalign(&raw_ptr, CACHE_LINE_BYTES, num_blocks * sizeof(cache_block_t)) != 0) {
        free(filter);
        return NULL;
    }

    filter->blocks = (cache_block_t*)raw_ptr;
    filter->num_blocks = num_blocks;
    filter->k_hashes = 8; // Оптимально: 8 бітів на кеш-лінію 512 бітів
    memset(filter->blocks, 0, num_blocks * sizeof(cache_block_t));

    return filter;
}

// Додавання 64-бітного ключа
void blocked_bloom_add(blocked_bloom_t *filter, uint64_t key) {
    uint64_t h1 = hash_step(key);
    uint64_t h2 = hash_step(h1 ^ 0x517cc1b727220a95ULL);

    // 1. Вибір одного 64-байтового блоку (кеш-лінії)
    size_t block_idx = h1 % filter->num_blocks;
    cache_block_t *block = &filter->blocks[block_idx];

    // 2. Встановлення k бітів ВИКЛЮЧНО всередині цієї кеш-лінії
    for (uint32_t i = 0; i < filter->k_hashes; ++i) {
        uint32_t bit_idx = (uint32_t)((h1 + i * h2) & (BITS_PER_BLOCK - 1));
        uint32_t word_idx = bit_idx >> 6;          // bit_idx / 64
        uint64_t bit_mask = 1ULL << (bit_idx & 63); // bit_idx % 64
        block->words[word_idx] |= bit_mask;
    }
}

// Перевірка наявності 64-бітного ключа
bool blocked_bloom_contains(const blocked_bloom_t *filter, uint64_t key) {
    uint64_t h1 = hash_step(key);
    uint64_t h2 = hash_step(h1 ^ 0x517cc1b727220a95ULL);

    // 1. Вибір блоку: єдине звернення до пам'яті
    size_t block_idx = h1 % filter->num_blocks;
    const cache_block_t *block = &filter->blocks[block_idx];

    // 2. Локальна перевірка всіх k бітів у L1 кеші
    for (uint32_t i = 0; i < filter->k_hashes; ++i) {
        uint32_t bit_idx = (uint32_t)((h1 + i * h2) & (BITS_PER_BLOCK - 1));
        uint32_t word_idx = bit_idx >> 6;
        uint64_t bit_mask = 1ULL << (bit_idx & 63);

        if ((block->words[word_idx] & bit_mask) == 0) {
            return false; // Гарантований True Negative (100% відсутній)
        }
    }
    return true; // Possible Positive (можливе хибнопозитивне)
}

void blocked_bloom_destroy(blocked_bloom_t *filter) {
    if (filter) {
        free(filter->blocks);
        free(filter);
    }
}
