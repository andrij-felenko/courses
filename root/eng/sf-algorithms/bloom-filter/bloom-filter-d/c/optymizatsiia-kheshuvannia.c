#include <stdint.h>
#include <stdbool.h>
#include <size_t.h>

/* Вставка ключа з оптимізацією Кірша-Мітценмахера */
void bloom_add_fast(uint8_t *bit_array, size_t num_bits, size_t k, uint64_t h1, uint64_t h2) {
    for (size_t i = 0; i < k; i++) {
        uint64_t bit_index = (h1 + i * h2) % num_bits;
        bit_array[bit_index >> 3] |= (uint8_t)(1u << (bit_index & 7));
    }
}

/* Перевірка наявності ключа */
bool bloom_check_fast(const uint8_t *bit_array, size_t num_bits, size_t k, uint64_t h1, uint64_t h2) {
    for (size_t i = 0; i < k; i++) {
        uint64_t bit_index = (h1 + i * h2) % num_bits;
        uint8_t byte = bit_array[bit_index >> 3];
        if ((byte & (1u << (bit_index & 7))) == 0) {
            return false; /* Гарантовано відсутній */
        }
    }
    return true; /* Імовірно присутній */
}
