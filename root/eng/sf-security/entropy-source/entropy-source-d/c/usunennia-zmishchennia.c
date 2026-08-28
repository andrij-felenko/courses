#include <stdint.h>
#include <stdbool.h>

/* Повертає true, якщо згенеровано новий вихідний біт */
bool von_neumann_extract(uint8_t b1, uint8_t b2, uint8_t *out_bit) {
    if (b1 == 0 && b2 == 1) {
        *out_bit = 0;
        return true;
    }
    if (b1 == 1 && b2 == 0) {
        *out_bit = 1;
        return true;
    }
    return false; /* 00 або 11 — скидання пари */
}
