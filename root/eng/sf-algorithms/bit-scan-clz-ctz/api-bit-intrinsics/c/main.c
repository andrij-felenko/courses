#include <stdint.h>
#include <stdbool.h>

/* Безпечне обчислення кількості провідних нулів у C з захистом від UB на нулі */
static inline uint32_t safe_countl_zero64(uint64_t x) {
    if (x == 0) {
        return 64;
    }
    return (uint32_t)__builtin_clzll(x);
}

/* Безпечне обчислення бітової ширини числа в C (аналог bit_width) */
static inline uint32_t safe_bit_width64(uint64_t x) {
    if (x == 0) {
        return 0;
    }
    return 64 - (uint32_t)__builtin_clzll(x);
}

/* Перевірка, чи є число степенем двійки в C (аналог has_single_bit) */
static inline bool safe_has_single_bit64(uint64_t x) {
    return x != 0 && (x & (x - 1)) == 0;
}

/* Округлення розміру буфера пам'яті вгору до найближчого степеня двійки */
static inline uint64_t safe_bit_ceil64(uint64_t x) {
    if (x <= 1) {
        return 1;
    }
    /* Захист від переповнення: якщо старший біт встановлений, округлити неможливо */
    if (x > (1ULL << 63)) {
        return 0;
    }
    int lz = __builtin_clzll(x - 1);
    return 1ULL << (64 - lz);
}
