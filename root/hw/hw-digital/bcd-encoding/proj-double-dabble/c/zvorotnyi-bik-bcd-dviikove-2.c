#include <stdint.h>

// digits[0] — найстарша цифра, count цифр. Повертає двійкове значення.
uint32_t bcd_digits_to_bin(const uint8_t *digits, uint8_t count) {
    uint32_t result = 0;
    for (uint8_t i = 0; i < count; ++i)     // від старшої цифри до молодшої
        result = result * 10 + digits[i];   // накопичуємо: ·10, тоді + цифра
    return result;
}
// {2,4,3}      -> 243
// {6,5,5,3,5}  -> 65535
