#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

/* Вбудована реалізація MurmurHash3_x64_128 для автономності прикладу */
static inline uint64_t rotl64(uint64_t x, int8_t r) {
    return (x << r) | (x >> (64 - r));
}

static void murmurhash3_x64_128(const void *key, const size_t len, const uint32_t seed, uint64_t out[2]) {
    const uint8_t *data = (const uint8_t *)key;
    const size_t nblocks = len / 16;

    uint64_t h1 = seed;
    uint64_t h2 = seed;

    const uint64_t c1 = 0x87c37b91114253d5ULL;
    const uint64_t c2 = 0x4cf5ad432745937fULL;

    const uint64_t *blocks = (const uint64_t *)(data);

    for (size_t i = 0; i < nblocks; i++) {
        uint64_t k1 = blocks[i * 2];
        uint64_t k2 = blocks[i * 2 + 1];

        k1 *= c1; k1 = rotl64(k1, 31); k1 *= c2; h1 ^= k1;
        h1 = rotl64(h1, 27); h1 += h2; h1 = h1 * 5 + 0x52dce729;

        k2 *= c2; k2 = rotl64(k2, 33); k2 *= c1; h2 ^= k2;
        h2 = rotl64(h2, 31); h2 += h1; h2 = h2 * 5 + 0x38495ab5;
    }

    const uint8_t *tail = (const uint8_t *)(data + nblocks * 16);
    uint64_t k1 = 0;
    uint64_t k2 = 0;

    switch (len & 15) {
        case 15: k2 ^= ((uint64_t)tail[14]) << 48;
        case 14: k2 ^= ((uint64_t)tail[13]) << 40;
        case 13: k2 ^= ((uint64_t)tail[12]) << 32;
        case 12: k2 ^= ((uint64_t)tail[11]) << 24;
        case 11: k2 ^= ((uint64_t)tail[10]) << 16;
        case 10: k2 ^= ((uint64_t)tail[9]) << 8;
        case  9: k2 ^= ((uint64_t)tail[8]) << 0;
                 k2 *= c2; k2 = rotl64(k2, 33); k2 *= c1; h2 ^= k2;
        case  8: k1 ^= ((uint64_t)tail[7]) << 56;
        case  7: k1 ^= ((uint64_t)tail[6]) << 48;
        case  6: k1 ^= ((uint64_t)tail[5]) << 40;
        case  5: k1 ^= ((uint64_t)tail[4]) << 32;
        case  4: k1 ^= ((uint64_t)tail[3]) << 24;
        case  3: k1 ^= ((uint64_t)tail[2]) << 16;
        case  2: k1 ^= ((uint64_t)tail[1]) << 8;
        case  1: k1 ^= ((uint64_t)tail[0]) << 0;
                 k1 *= c1; k1 = rotl64(k1, 31); k1 *= c2; h1 ^= k1;
    }

    h1 ^= len; h2 ^= len;
    h1 += h2; h2 += h1;

    h1 ^= h1 >> 33; h1 *= 0xff51afd7ed558ccdULL;
    h1 ^= h1 >> 33; h1 *= 0xc4ceb9fe1a85ec53ULL;
    h1 ^= h1 >> 33;

    h2 ^= h2 >> 33; h2 *= 0xff51afd7ed558ccdULL;
    h2 ^= h2 >> 33; h2 *= 0xc4ceb9fe1a85ec53ULL;
    h2 ^= h2 >> 33;

    h1 += h2; h2 += h1;

    out[0] = h1;
    out[1] = h2;
}

/* Структура фільтра Блума у стилі C */
typedef struct {
    uint8_t *bit_array;
    size_t num_bits;
    size_t num_hashes;
    size_t item_count;
} bloom_filter_t;

/* Ініціалізація за розрахованими параметрами m та k */
bloom_filter_t *bloom_create(size_t num_bits, size_t num_hashes) {
    if (num_bits == 0 || num_hashes == 0) return NULL;

    bloom_filter_t *filter = (bloom_filter_t *)malloc(sizeof(bloom_filter_t));
    if (!filter) return NULL;

    size_t byte_count = (num_bits + 7) / 8;
    filter->bit_array = (uint8_t *)calloc(byte_count, sizeof(uint8_t));
    if (!filter->bit_array) {
        free(filter);
        return NULL;
    }

    filter->num_bits = num_bits;
    filter->num_hashes = num_hashes;
    filter->item_count = 0;
    return filter;
}

/* Створення з автоматичним розрахунком m та k за n та p */
bloom_filter_t *bloom_create_optimal(size_t expected_items, double false_positive_rate) {
    if (expected_items == 0 || false_positive_rate <= 0.0 || false_positive_rate >= 1.0) {
        return NULL;
    }

    double num_bits_d = -((double)expected_items * log(false_positive_rate)) / (log(2.0) * log(2.0));
    size_t num_bits = (size_t)ceil(num_bits_d);

    double num_hashes_d = ((double)num_bits / (double)expected_items) * log(2.0);
    size_t num_hashes = (size_t)round(num_hashes_d);
    if (num_hashes < 1) num_hashes = 1;

    return bloom_create(num_bits, num_hashes);
}

void bloom_destroy(bloom_filter_t *filter) {
    if (!filter) return;
    free(filter->bit_array);
    free(filter);
}

void bloom_clear(bloom_filter_t *filter) {
    if (!filter) return;
    size_t byte_count = (filter->num_bits + 7) / 8;
    memset(filter->bit_array, 0, byte_count);
    filter->item_count = 0;
}

/* Додавання елемента до бітового масиву */
void bloom_add(bloom_filter_t *filter, const void *key, size_t len) {
    if (!filter || !key || len == 0) return;

    uint64_t hash_out[2];
    murmurhash3_x64_128(key, len, 0x9773b15d, hash_out);

    uint64_t h1 = hash_out[0];
    uint64_t h2 = hash_out[1];

    for (size_t i = 0; i < filter->num_hashes; i++) {
        uint64_t bit_index = (h1 + i * h2) % filter->num_bits;
        filter->bit_array[bit_index >> 3] |= (1u << (bit_index & 7));
    }
    filter->item_count++;
}

/* Перевірка належності елемента */
bool bloom_check(const bloom_filter_t *filter, const void *key, size_t len) {
    if (!filter || !key || len == 0) return false;

    uint64_t hash_out[2];
    murmurhash3_x64_128(key, len, 0x9773b15d, hash_out);

    uint64_t h1 = hash_out[0];
    uint64_t h2 = hash_out[1];

    for (size_t i = 0; i < filter->num_hashes; i++) {
        uint64_t bit_index = (h1 + i * h2) % filter->num_bits;
        if (!(filter->bit_array[bit_index >> 3] & (1u << (bit_index & 7)))) {
            return false; /* Знайдено 0 -> елемента ТОЧНО немає */
        }
    }
    return true; /* Усі біти 1 -> елемент ЙМОВІРНО є */
}

double bloom_current_fp_rate(const bloom_filter_t *filter) {
    if (!filter || filter->num_bits == 0) return 1.0;
    double kn = (double)(filter->num_hashes * filter->item_count);
    double m = (double)filter->num_bits;
    return pow(1.0 - exp(-kn / m), (double)filter->num_hashes);
}
