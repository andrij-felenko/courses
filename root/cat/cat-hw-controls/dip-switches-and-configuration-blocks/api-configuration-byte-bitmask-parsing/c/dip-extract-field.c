#include <stdint.h>
#include <stdbool.h>

#define DIP_MAKE_MASK(width, shift) (((1U << (width)) - 1U) << (shift))

// Витягування значення бітового суб-поля з нормалізованого байта
uint8_t dip_extract_field(uint8_t norm_byte, uint8_t width, uint8_t shift) {
    uint8_t mask = DIP_MAKE_MASK(width, shift);
    return (norm_byte & mask) >> shift;
}

// Перевірка стану однобітового прапорця
bool dip_extract_flag(uint8_t norm_byte, uint8_t bit_index) {
    return (norm_byte & (1U << bit_index)) != 0;
}
