#include <immintrin.h>
#include <stdint.h>
#include <stddef.h>

void butterfly_avx2(uint32_t *a, size_t j, size_t t, __m256i mod_vec) {
    __m256i u = _mm256_loadu_si256((const __m256i *)&a[j]);
    __m256i v = _mm256_loadu_si256((const __m256i *)&a[j + t]);

    /* Поелементне модульне додавання u + v mod p */
    __m256i sum = _mm256_add_epi32(u, v);
    __m256i mask_sum = _mm256_cmpgt_epi32(sum, mod_vec);
    __m256i res_add = _mm256_sub_epi32(sum, _mm256_and_si256(mask_sum, mod_vec));

    /* Модульне віднімання з додаванням константи модуля */
    __m256i diff = _mm256_sub_epi32(_mm256_add_epi32(u, mod_vec), v);
    __m256i mask_diff = _mm256_cmpgt_epi32(diff, mod_vec);
    __m256i res_sub = _mm256_sub_epi32(diff, _mm256_and_si256(mask_diff, mod_vec));

    _mm256_storeu_si256((__m256i *)&a[j], res_add);
    _mm256_storeu_si256((__m256i *)&a[j + t], res_sub);
}
