/* pc64.h — скільки одиниць у 64-бітному слові */
#ifndef PC64_H
#define PC64_H
#include <stdint.h>

static inline int pc64_swar(uint64_t x) {
    x = x - ((x >> 1) & 0x5555555555555555ULL);
    x = (x & 0x3333333333333333ULL) + ((x >> 2) & 0x3333333333333333ULL);
    x = (x + (x >> 4)) & 0x0F0F0F0F0F0F0F0FULL;
    return (int)((x * 0x0101010101010101ULL) >> 56);
}

#if defined(__cplusplus) && __cplusplus >= 202002L
#  include <version>          /* саме тут оголошено __cpp_lib_bitops */
#endif

#if defined(__cpp_lib_bitops)
#  include <bit>
   static inline int pc64(uint64_t x) { return std::popcount(x); }
#elif defined(__GNUC__)                       /* GCC і Clang */
   static inline int pc64(uint64_t x) { return __builtin_popcountll(x); }
#elif defined(_MSC_VER) && defined(_M_X64)
#  include <intrin.h>
   static inline int pc64(uint64_t x) { return (int)__popcnt64(x); }
#else
   static inline int pc64(uint64_t x) { return pc64_swar(x); }
#endif

#endif
