#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>

/* Векторизоване заповнення рівня таблиці за допомогою AVX2 */
void st_build_level_avx2(int32_t *dest, const int32_t *src, size_t half, size_t count) {
    size_t i = 0;
    
    /* Обробка блоками по 8 елементів (256 біт) */
    for (; i + 8 <= count; i += 8) {
        __m256i va = _mm256_loadu_si256((const __m256i *)(src + i));
        __m256i vb = _mm256_loadu_si256((const __m256i *)(src + i + half));
        __m256i vmin = _mm256_min_epi32(va, vb);
        _mm256_storeu_si256((__m256i *)(dest + i), vmin);
    }
    
    /* Хвіст масиву для елементів, що не кратні 8 */
    for (; i < count; ++i) {
        dest[i] = (src[i] < src[i + half]) ? src[i] : src[i + half];
    }
}
