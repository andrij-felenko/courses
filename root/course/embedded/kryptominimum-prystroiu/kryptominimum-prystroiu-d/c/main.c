#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

// Гарантоване занулення пам'яті, яке не видаляється оптимізатором (-O2/-O3)
void secure_memzero(void *ptr, size_t len) {
    volatile uint8_t *p = (volatile uint8_t *)ptr;
    while (len--) {
        *p++ = 0;
    }
}

// Порівняння масивів за постійний час: захист від таймінгових атак
bool constant_time_memcmp(const void *a, const void *b, size_t len) {
    const uint8_t *pa = (const uint8_t *)a;
    const uint8_t *pb = (const uint8_t *)b;
    uint8_t result = 0;

    for (size_t i = 0; i < len; i++) {
        result |= (pa[i] ^ pb[i]);
    }

    return (result == 0);
}

// Дерандомізатор фон Неймана для потоку бітів з аналогового TRNG
// Повертає кількість отриманих чистих бітів (0 або 1)
bool von_neumann_step(uint8_t bit_pair, uint8_t *out_bit) {
    uint8_t b0 = (bit_pair >> 1) & 0x01;
    uint8_t b1 = bit_pair & 0x01;

    if (b0 == 0 && b1 == 1) {
        *out_bit = 0;
        return true;
    } else if (b0 == 1 && b1 == 0) {
        *out_bit = 1;
        return true;
    }
    // Пари 00 та 11 відкидаються для усунення bias
    return false;
}
