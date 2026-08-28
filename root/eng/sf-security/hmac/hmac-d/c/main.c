#include <stdint.h>
#include <stddef.h>

/* Безпечне константне порівняння масивів однакової довжини */
int constant_time_memcmp(const void *a, const void *b, size_t len) {
    const volatile uint8_t *p1 = (const volatile uint8_t *)a;
    const volatile uint8_t *p2 = (const volatile uint8_t *)b;
    uint8_t diff = 0;

    for (size_t i = 0; i < len; ++i) {
        diff |= (p1[i] ^ p2[i]);
    }

    /* Повертає 1 при повній ідентичності, 0 при будь-якій розбіжності */
    return (diff == 0);
}
