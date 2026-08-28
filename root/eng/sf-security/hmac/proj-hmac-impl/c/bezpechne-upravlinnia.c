#include <stdint.h>
#include <stddef.h>
#include <string.h>

/* Безпечне затирання пам'яті в C, стійке до Dead Store Elimination */
void secure_memzero(void *v, size_t n) {
    volatile uint8_t *p = (volatile uint8_t *)v;
    while (n--) {
        *p++ = 0;
    }
}
