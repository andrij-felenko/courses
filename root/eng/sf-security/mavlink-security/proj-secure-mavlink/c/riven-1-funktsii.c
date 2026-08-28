#include <stdint.h>
#include <stddef.h>
#include <string.h>

// Порівняння двох масивів пам'яті за строго постійний час
int secure_memcmp(const void *a, const void *b, size_t len) {
    const uint8_t *p1 = (const uint8_t *)a;
    const uint8_t *p2 = (const uint8_t *)b;
    uint8_t result = 0;

    for (size_t i = 0; i < len; ++i) {
        result |= (p1[i] ^ p2[i]);
    }

    return (result == 0) ? 0 : -1;
}

// Гарантоване затирання конфіденційних даних у пам'яті (захист від оптимізації компілятора)
void secure_zeroize(void *ptr, size_t len) {
    volatile uint8_t *p = (volatile uint8_t *)ptr;
    while (len--) {
        *p++ = 0;
    }
}
