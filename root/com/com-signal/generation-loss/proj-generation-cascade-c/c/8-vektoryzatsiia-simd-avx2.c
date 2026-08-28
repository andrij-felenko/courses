// C99: Симуляція векторизованого квантування AVX2
__m256d v_step = _mm256_set1_pd(step);
__m256d v_inv_step = _mm256_set1_pd(1.0 / step);

for (size_t i = 0; i < len; i += 4) {
    __m256d v_data = _mm256_loadu_pd(&buf[i]);
    __m256d v_scaled = _mm256_mul_pd(v_data, v_inv_step);
    __m256d v_rounded = _mm256_round_pd(v_scaled, _MM_FROUND_TO_NEAREST_INT | _MM_FROUND_NO_EXC);
    __m256d v_quant = _mm256_mul_pd(v_rounded, v_step);
    _mm256_storeu_pd(&buf[i], v_quant);
}
