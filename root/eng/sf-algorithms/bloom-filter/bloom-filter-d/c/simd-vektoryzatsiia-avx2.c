#include <immintrin.h>
#include <stdint.h>

/* SIMD-векторизоване обчислення індексів у C */
void bloom_check_simd_avx2(const uint8_t *bit_array, const uint64_t *h1_vec, const uint64_t *h2_vec, uint32_t *results) {
    __m256i v_h1 = _mm256_loadu_si256((const __m256i*)h1_vec);
    __m256i v_h2 = _mm256_loadu_si256((const __m256i*)h2_vec);
    __m256i v_idx = _mm256_add_epi64(v_h1, v_h2);
    /* Пакетизоване зчитування 4х64-бітних індексів за один такт */
    _mm256_storeu_si256((__m256i*)results, v_idx);
}
