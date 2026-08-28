#include <stdint.h>
#include <stddef.h>

/**
 * Гарантоване затирання конфіденційних даних у пам'яті (C).
 * Запобігає оптимізації Dead Store Elimination за допомогою volatile та бар'єра.
 */
void crypto_secure_wipe(void *v, size_t n) {
    if (v == NULL || n == 0) {
        return;
    }
    
    volatile uint8_t *p = (volatile uint8_t *)v;
    while (n--) {
        *p++ = 0x00;
    }

    #if defined(__GNUC__) || defined(__clang__)
    __asm__ __volatile__("" : : "r"(v) : "memory");
    #endif
}

/**
 * Порівняння двох блоків пам'яті за строго константний час (C).
 * Захищає від атак за часом виконання (Timing Attacks).
 */
int crypto_constant_time_equals(const void *a, const void *b, size_t n) {
    if (a == NULL || b == NULL) {
        return 0;
    }

    const volatile uint8_t *pa = (const volatile uint8_t *)a;
    const volatile uint8_t *pb = (const volatile uint8_t *)b;
    volatile uint8_t result = 0;

    for (size_t i = 0; i < n; i++) {
        result |= (pa[i] ^ pb[i]);
    }

    return (result == 0);
}
