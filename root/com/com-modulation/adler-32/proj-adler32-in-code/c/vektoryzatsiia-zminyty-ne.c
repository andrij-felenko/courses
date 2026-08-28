#include <immintrin.h>   /* SSSE3 */

/* Доливає рівно 16 байтів у a і b — без жодного зведення за модулем. */
static inline void adler_block16(const uint8_t *d, uint32_t *a, uint32_t *b) {
    const __m128i zero = _mm_setzero_si128();
    const __m128i ones = _mm_set1_epi16(1);
    /* ваги 16,15,…,1 — саме в тому порядку, в якому байти лежать у пам'яті */
    const __m128i w = _mm_setr_epi8(16, 15, 14, 13, 12, 11, 10, 9,
                                     8,  7,  6,  5,  4,  3,  2, 1);

    __m128i v = _mm_loadu_si128((const __m128i *)d);

    *b += 16u * (*a);                              /* доданок k·A — на старому A! */

    __m128i s = _mm_sad_epu8(v, zero);             /* Σ dⱼ: дві часткові суми */
    s = _mm_add_epi32(s, _mm_srli_si128(s, 8));    /* склали половини */
    *a += (uint32_t)_mm_cvtsi128_si32(s);

    __m128i t = _mm_maddubs_epi16(v, w);           /* Σ (16−j)·dⱼ: 8 лічб по 16 біт */
    t = _mm_madd_epi16(t, ones);                   /* розширили до 4 лічб по 32 біти */
    t = _mm_add_epi32(t, _mm_srli_si128(t, 8));
    t = _mm_add_epi32(t, _mm_srli_si128(t, 4));
    *b += (uint32_t)_mm_cvtsi128_si32(t);
}
