#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>

#if defined(_MSC_VER)
#include <intrin.h>
static inline int ctz64(uint64_t mask) {
    unsigned long idx;
    _BitScanForward64(&idx, mask);
    return (int)idx;
}
#else
static inline int ctz64(uint64_t mask) {
    return __builtin_ctzll(mask);
}
#endif

/* Демонстрація вилучення структурних токенів через бітову маску */
int main(void) {
    /* 
       Вхідний рядок (16 байтів):  { "a" : [ 1 , 2 ] }
       Позиції:                    0 123 4 5 6 7 8 9 0
    */
    uint64_t candidate_mask = (1ULL << 0) | (1ULL << 4) | (1ULL << 5) | 
                              (1ULL << 7) | (1ULL << 9) | (1ULL << 10);
    uint64_t in_string_mask = (1ULL << 2); /* символ 'a' всередині лапок */

    /* Вилучення токенів поза рядками */
    uint64_t structural_mask = candidate_mask & (~in_string_mask);

    printf("Знайдені індекси структурних токенів: ");
    while (structural_mask != 0) {
        int idx = ctz64(structural_mask);
        printf("%d ", idx);
        structural_mask &= (structural_mask - 1); /* Скидання молодшого біта */
    }
    printf("\n");

    return 0;
}
