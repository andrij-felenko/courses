#include <immintrin.h>
#include <span>
#include <cmath>
#include <cstddef>

/* Векторизоване обчислення скалярного добутку на C++20 */
[[nodiscard]] double avx2_fma_dot_product(std::span<const double> a,
                                          std::span<const double> b) noexcept {
    const size_t n = a.size();
    if (n != b.size() || n == 0) return 0.0;

    size_t i = 0;
    __m256d acc0 = _mm256_setzero_pd();
    __m256d acc1 = _mm256_setzero_pd();
    __m256d acc2 = _mm256_setzero_pd();
    __m256d acc3 = _mm256_setzero_pd();

    for (; i + 15 < n; i += 16) {
        const __m256d va0 = _mm256_loadu_pd(a.data() + i);
        const __m256d vb0 = _mm256_loadu_pd(b.data() + i);
        acc0 = _mm256_fmadd_pd(va0, vb0, acc0);

        const __m256d va1 = _mm256_loadu_pd(a.data() + i + 4);
        const __m256d vb1 = _mm256_loadu_pd(b.data() + i + 4);
        acc1 = _mm256_fmadd_pd(va1, vb1, acc1);

        const __m256d va2 = _mm256_loadu_pd(a.data() + i + 8);
        const __m256d vb2 = _mm256_loadu_pd(b.data() + i + 8);
        acc2 = _mm256_fmadd_pd(va2, vb2, acc2);

        const __m256d va3 = _mm256_loadu_pd(a.data() + i + 12);
        const __m256d vb3 = _mm256_loadu_pd(b.data() + i + 12);
        acc3 = _mm256_fmadd_pd(va3, vb3, acc3);
    }

    const __m256d sum_acc = _mm256_add_pd(_mm256_add_pd(acc0, acc1),
                                          _mm256_add_pd(acc2, acc3));

    const __m128d hi128 = _mm256_extractf128_pd(sum_acc, 1);
    const __m128d lo128 = _mm256_castpd256_pd128(sum_acc);
    const __m128d sum128 = _mm_add_pd(lo128, hi128);
    const __m128d hi64 = _mm_unpackhi_pd(sum128, sum128);
    double total = _mm_cvtsd_f64(_mm_add_sd(sum128, hi64));

    for (; i < n; ++i) {
        total = std::fma(a[i], b[i], total);
    }

    return total;
}
