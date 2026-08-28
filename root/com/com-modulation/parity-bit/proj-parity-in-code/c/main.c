#include <stdint.h>
#include <stdbool.h>

// 1 — якщо серед одиниць байта непарне число (XOR усіх бітів)
static inline uint8_t parity_of(uint8_t b) {
    b ^= b >> 4;
    b ^= b >> 2;
    b ^= b >> 1;
    return b & 1u;
}

typedef enum { PARITY_EVEN, PARITY_ODD } parity_mode_t;

// Пакуємо 7 біт даних (0..0x7F) + біт парності у старший (8-й) розряд.
// even: загальна кількість одиниць у байті парна; odd: непарна.
uint8_t parity_encode(uint8_t data7, parity_mode_t mode) {
    uint8_t p = parity_of(data7 & 0x7Fu);   // парність самих даних
    if (mode == PARITY_ODD) p ^= 1u;        // для odd інвертуємо домовленість
    return (uint8_t)((p << 7) | (data7 & 0x7Fu));
}

// true — слово ціле за обраною домовленістю; false — помилка виявлена.
bool parity_check(uint8_t word, parity_mode_t mode) {
    uint8_t ones_odd = parity_of(word);     // парність усіх 8 бітів разом
    // even-домовленість вимагає парної суми (ones_odd == 0);
    // odd-домовленість вимагає непарної (ones_odd == 1).
    return ones_odd == (mode == PARITY_ODD ? 1u : 0u);
}
