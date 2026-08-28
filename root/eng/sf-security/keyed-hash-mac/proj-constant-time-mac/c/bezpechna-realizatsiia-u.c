#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

/* БЕЗПЕЧНО: Константний час порівняння без витоку затримки */
bool constant_time_memcmp(const uint8_t *a, const uint8_t *b, size_t len) {
    /* volatile забороняє оптимізатору компілятора вставити ранній вихід */
    volatile uint8_t diff = 0;
    
    for (size_t i = 0; i < len; ++i) {
        diff |= (uint8_t)(a[i] ^ b[i]);
    }
    
    return diff == 0;
}
