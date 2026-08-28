#include <stdint.h>
#include <stddef.h>

/* Умовна перестановка двох 64-бітних слів */
void ct_cswap_u64(uint64_t condition, uint64_t *a, uint64_t *b) {
    uint64_t mask = -condition;
    #if defined(__GNUC__) || defined(__clang__)
    __asm__ volatile ("" : "+r" (mask));
    #endif
    uint64_t delta = mask & (*a ^ *b);
    *a ^= delta;
    *b ^= delta;
}

/* Умовна перестановка масивів великих чисел (наприклад, 256-бітних координат точок кривої) */
void ct_cswap_arrays(uint8_t condition, uint8_t *a, uint8_t *b, size_t len) {
    uint8_t mask = (uint8_t)(-(int8_t)condition);
    #if defined(__GNUC__) || defined(__clang__)
    __asm__ volatile ("" : "+r" (mask));
    #endif
    for (size_t i = 0; i < len; ++i) {
        uint8_t delta = mask & (a[i] ^ b[i]);
        a[i] ^= delta;
        b[i] ^= delta;
    }
}
