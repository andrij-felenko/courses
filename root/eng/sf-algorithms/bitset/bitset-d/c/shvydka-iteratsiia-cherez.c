#include <stdint.h>
#include <stdio.h>

void iterate_bitset_word(uint64_t word, size_t word_base_index) {
    while (word != 0) {
        int bit_offset = __builtin_ctzll(word);
        size_t element = word_base_index + (size_t)bit_offset;
        printf("Знайдено елемент: %zu\n", element);
        
        /* Скидаємо оброблений молодший біт */
        word &= (word - 1);
    }
}
