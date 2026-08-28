// C AVX2 vector intrinsic calculation for 4 points in parallel
#include <immintrin.h>

void calc_speed_air_avx2(const double* temps, double* speeds, size_t count) {
    const __m256d v_one = _mm256_set1_pd(1.0);
    const __m256d v_inv273 = _mm256_set1_pd(1.0 / 273.15);
    const __m256d v_c0 = _mm256_set1_pd(331.3);

    for (size_t i = 0; i < count; i += 4) {
        __m256d v_t = _mm256_loadu_pd(&temps[i]);
        __m256d v_term = _mm256_fmadd_pd(v_t, v_inv273, v_one); // 1 + t/273.15
        __m256d v_sqrt = _mm256_sqrt_pd(v_term);
        __m256d v_c = _mm256_mul_pd(v_c0, v_sqrt);
        _mm256_storeu_pd(&speeds[i], v_c);
    }
}
