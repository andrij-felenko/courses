// Приклад бітового перетину рядків u та v за допомогою AVX2 інструкцій
void intersect_rows_avx2(const uint64_t* row_u, const uint64_t* row_v, 
                         uint64_t* result, size_t words) {
    size_t i = 0;
    for (; i + 4 <= words; i += 4) {
        // Завантажуємо по 256 бітів (4 слова по 64 біти) у SIMD-регістри
        __m256i a = _mm256_loadu_si256((const __m256i*)&row_u[i]);
        __m256i b = _mm256_loadu_si256((const __m256i*)&row_v[i]);
        __m256i res = _mm256_and_si256(a, b);
        _mm256_storeu_si256((__m256i*)&result[i], res);
    }
    // Хвіст обробляємо звичайним циклом
    for (; i < words; ++i) {
        result[i] = row_u[i] & row_v[i];
    }
}
