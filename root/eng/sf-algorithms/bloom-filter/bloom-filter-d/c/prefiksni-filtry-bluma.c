#include <stdint.h>
#include <string.h>

/* Вставка префіксного ключа у фільтр */
void bloom_add_prefix(uint8_t *bit_array, size_t m, size_t k, const char *key, size_t prefix_len) {
    uint64_t h1 = murmurhash3_x64_64(key, prefix_len, 0x9773b15d);
    uint64_t h2 = murmurhash3_x64_64(key, prefix_len, 0x1cbd4317);
    for (size_t i = 0; i < k; i++) {
        size_t idx = (h1 + i * h2) % m;
        bit_array[idx >> 3] |= (uint8_t)(1u << (idx & 7));
    }
}
