#include <immintrin.h>
#include <stdint.h>

// Використання спеціальних апаратних інтринсиків без переміщення пам'яті
__m128i mask_float_vector_c(__m128 vf) {
    // _mm_castps_si128 - це нуль-інструкційний каст на рівні регістрів
    __m128i vi = _mm_castps_si128(vf);
    __m128i mask = _mm_set1_epi32(0x7FFFFFFF); // Маска скидання знаку (fabs)
    return _mm_and_si128(vi, mask);
}
