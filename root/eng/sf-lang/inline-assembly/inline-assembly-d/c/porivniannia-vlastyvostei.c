#include <stdint.h>
#include <immintrin.h>

/* Спосіб 1: Через вбудований асемблер (неефективно при константах) */
int popcount_asm(uint64_t val) {
    uint64_t count;
    __asm__ ("popcntq %1, %0" : "=r" (count) : "r" (val) : "cc");
    return (int)count;
}

/* Спосіб 2: Через intrinsic-функцію GCC/Clang/MSVC (оптимально) */
int popcount_intrinsic(uint64_t val) {
    #if defined(_MSC_VER)
        return (int)__popcnt64(val);
    #else
        return __builtin_popcountll(val);
    #endif
}
