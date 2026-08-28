#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Безпечне константне порівняння двох буферів */
bool secure_memequal(const void *b1, const void *b2, size_t len) {
    const uint8_t *p1 = (const uint8_t *)b1;
    const uint8_t *p2 = (const uint8_t *)b2;
    uint8_t diff = 0;

    for (size_t i = 0; i < len; ++i) {
        diff |= (p1[i] ^ p2[i]);
    }

    /* Компіляторний бар'єр: блокує видалення акумуляції */
    __asm__ __volatile__("" : "+r"(diff) : : "memory");

    return (diff == 0);
}

/* Безгалузевий вибір між двома 32-бітними числами */
uint32_t secure_select32(uint32_t choice_bit, uint32_t val_true, uint32_t val_false) {
    /* Формуємо маску 0xFFFFFFFF або 0x00000000 */
    uint32_t mask = (uint32_t)(-(int32_t)(choice_bit & 1));
    return (val_true & mask) | (val_false & ~mask);
}
