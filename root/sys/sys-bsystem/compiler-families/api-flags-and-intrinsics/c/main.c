#include <stdint.h>

#if defined(_MSC_VER) && !defined(__clang__)
#include <intrin.h>

static inline uint32_t count_leading_zeros32(uint32_t x) {
    if (x == 0) return 32;
    unsigned long index;
    _BitScanReverse(&index, x);
    return 31 - index;
}

static inline uint32_t popcount32(uint32_t x) {
    return __popcnt(x);
}

#else

static inline uint32_t count_leading_zeros32(uint32_t x) {
    if (x == 0) return 32;
    return (uint32_t)__builtin_clz(x);
}

static inline uint32_t popcount32(uint32_t x) {
    return (uint32_t)__builtin_popcount(x);
}

#endif
