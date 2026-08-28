#include <stdint.h>
#include <stddef.h>

/* Бар'єр компілятора: запобігає перетворенню побітової маски на умовні стрибки */
static inline uint32_t ct_barrier_u32(uint32_t x) {
    #if defined(__GNUC__) || defined(__clang__)
    __asm__ volatile ("" : "+r" (x));
    #endif
    return x;
}

static inline uint8_t ct_barrier_u8(uint8_t x) {
    #if defined(__GNUC__) || defined(__clang__)
    __asm__ volatile ("" : "+r" (x));
    #endif
    return x;
}

/* Умовний вибір 32-бітного слова: повертає x, якщо condition == 1, інакше y */
uint32_t ct_select_u32(uint32_t condition, uint32_t x, uint32_t y) {
    uint32_t mask = -condition;
    mask = ct_barrier_u32(mask);
    return y ^ (mask & (x ^ y));
}

/* Умовний вибір для 8-бітного байта */
uint8_t ct_select_u8(uint8_t condition, uint8_t x, uint8_t y) {
    uint8_t mask = (uint8_t)(-(int8_t)condition);
    mask = ct_barrier_u8(mask);
    return (uint8_t)(y ^ (mask & (x ^ y)));
}

/* Умовне копіювання буфера: якщо condition == 1, dst = src, інакше dst не змінюється */
void ct_select_buffer(uint8_t condition, uint8_t *dst, const uint8_t *src, size_t len) {
    uint8_t mask = (uint8_t)(-(int8_t)condition);
    mask = ct_barrier_u8(mask);
    for (size_t i = 0; i < len; ++i) {
        dst[i] ^= mask & (src[i] ^ dst[i]);
    }
}
