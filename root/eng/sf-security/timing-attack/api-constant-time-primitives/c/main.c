#include <stdint.h>
#include <stddef.h>

/* Перетворення булевого прапорця (0 або 1) на бітову маску (0x00..0 або 0xFF..F) */
static inline uint32_t ct_bool_to_mask32(uint32_t bit) {
    return (uint32_t)(-(int32_t)(bit & 1));
}

/* Перевірка на нуль: повертає маску 0xFFFFFFFF якщо val == 0, інакше 0x00000000 */
static inline uint32_t ct_is_zero_mask32(uint32_t val) {
    uint64_t v = val;
    return (uint32_t)(~((v | (0 - v)) >> 31) & 1) ? 0xFFFFFFFFU : 0x00000000U;
}

/* Безгалузевий мультиплексор: якщо mask == 0xFFFFFFFF, повертає a, якщо 0, повертає b */
static inline uint32_t ct_select32(uint32_t mask, uint32_t a, uint32_t b) {
    return (a & mask) | (b & ~mask);
}

/* Умовне копіювання буфера: якщо flag == 1, копіює src в dst, інакше dst не змінюється */
static inline void ct_conditional_copy(uint8_t flag, uint8_t *dst, const uint8_t *src, size_t len) {
    uint8_t mask = (uint8_t)(-(int8_t)(flag & 1));
    for (size_t i = 0; i < len; ++i) {
        dst[i] ^= mask & (src[i] ^ dst[i]);
    }
    /* Компіляторний бар'єр пам'яті */
    __asm__ __volatile__("" : "+m"(*dst) : : "memory");
}

/* Умовний обмін двох буферів (Conditional Swap) за константний час */
static inline void ct_conditional_swap(uint8_t flag, uint8_t *a, uint8_t *b, size_t len) {
    uint8_t mask = (uint8_t)(-(int8_t)(flag & 1));
    for (size_t i = 0; i < len; ++i) {
        uint8_t delta = mask & (a[i] ^ b[i]);
        a[i] ^= delta;
        b[i] ^= delta;
    }
    __asm__ __volatile__("" : "+m"(*a), "+m"(*b) : : "memory");
}
