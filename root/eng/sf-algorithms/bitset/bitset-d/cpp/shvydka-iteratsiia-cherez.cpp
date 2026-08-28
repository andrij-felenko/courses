#include <cstdint>
#include <bit>
#include <iostream>

void iterate_bitset_word(std::uint64_t word, std::size_t word_base_index) {
    while (word != 0) {
        int bit_offset = std::countr_zero(word);
        std::size_t element = word_base_index + static_cast<std::size_t>(bit_offset);
        std::cout << "Знайдено елемент: " << element << "\n";
        
        word &= (word - 1);
    }
}
