// Приклад SIMD-ініціалізації за допомогою інтринсиків AVX2
#include <immintrin.h>

void fast_dsu_init(int* parent, std::size_t n) {
    std::size_t i = 0;
    __m256i step = _mm256_set1_epi32(8);
    __m256i curr = _mm256_set_epi32(7, 6, 5, 4, 3, 2, 1, 0);

    for (; i + 7 < n; i += 8) {
        _mm256_storeu_si256(reinterpret_cast<__m256i*>(parent + i), curr);
        curr = _mm256_add_epi32(curr, step);
    }
    for (; i < n; ++i) {
        parent[i] = static_cast<int>(i);
    }
}
