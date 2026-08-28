#include <stdint.h>
#include <string.h>

// Перетворює число будь-якої ширини у DIGITS десяткових цифр.
// digits[0] — найстарша цифра. Викликач дає масив достатнього розміру:
//   DIGITS >= ceil(NBITS * 0.30103).
void bin_to_bcd_n(uint32_t value, uint8_t *digits, uint8_t DIGITS, uint8_t NBITS) {
    memset(digits, 0, DIGITS);                 // поле цифр — усі нулі

    for (int8_t i = NBITS - 1; i >= 0; --i) {
        // 1) корекція наперед: кожній цифрі >= 5 додати 3
        for (uint8_t d = 0; d < DIGITS; ++d)
            if (digits[d] >= 5) digits[d] += 3;

        // 2) зсув усього поля вліво на 1 біт, з переносом між цифрами
        uint8_t carry = (value >> i) & 1;      // біт числа входить у наймолодшу цифру
        for (int8_t d = DIGITS - 1; d >= 0; --d) {
            uint8_t v = (uint8_t)((digits[d] << 1) | carry);  // подвоїли й влили перенос знизу
            digits[d] = v & 0xF;               // лишили тетраду
            carry     = v >> 4;                // старший біт -> перенос у сусідню цифру
        }
    }
}

// приклад: bin_to_bcd_n(65535, d, 5, 16) -> d = {6,5,5,3,5}
//          bin_to_bcd_n(1000,  d, 4, 16) -> d = {1,0,0,0}
