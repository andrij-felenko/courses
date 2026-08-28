#include <stdint.h>
#include <stddef.h>

void partitioned_bloom_add(uint8_t *bits, size_t section_size_bits, size_t k, uint64_t h1, uint64_t h2) {
    for (size_t i = 0; i < k; i++) {
        size_t bit_in_section = (h1 + i * h2) % section_size_bits;
        size_t global_bit = i * section_size_bits + bit_in_section;
        bits[global_bit >> 3] |= (uint8_t)(1u << (global_bit & 7));
    }
}
