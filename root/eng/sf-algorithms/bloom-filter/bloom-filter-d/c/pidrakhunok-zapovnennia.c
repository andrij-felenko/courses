#include <stdint.h>
#include <size_t.h>

/* Високопродуктивний підрахунок одиничних бітів через POPCNT */
size_t bloom_count_set_bits(const uint8_t *bit_array, size_t bytes) {
    size_t total_set = 0;
    size_t i = 0;
    const uint64_t *ptr64 = (const uint64_t *)bit_array;
    size_t words64 = bytes / 8;
    for (; i < words64; i++) {
        total_set += (size_t)__builtin_popcountll(ptr64[i]);
    }
    for (size_t j = words64 * 8; j < bytes; j++) {
        total_set += (size_t)__builtin_popcount(bit_array[j]);
    }
    return total_set;
}
