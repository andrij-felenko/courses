#include <immintrin.h>
#include <stddef.h>

/* Векторизоване обчислення скалярного добутку з розгортанням на 4 акумулятори */
double avx2_fma_dot_product(const double* a, const double* b, size_t n) {
    size_t i = 0;
    __m256d acc0 = _mm256_setzero_pd();
    __m256d acc1 = _mm256_setzero_pd();
    __m256d acc2 = _mm256_setzero_pd();
    __m256d acc3 = _mm256_setzero_pd();

    /* Основний цикл: обробка по 16 елементів за ітерацію */
    for (; i + 15 < n; i += 16) {
        __m256d va0 = _mm256_loadu_pd(a + i);
        __m256d vb0 = _mm256_loadu_pd(b + i);
        acc0 = _mm256_fmadd_pd(va0, vb0, acc0);

        __m256d va1 = _mm256_loadu_pd(a + i + 4);
        __m256d vb1 = _mm256_loadu_pd(b + i + 4);
        acc1 = _mm256_fmadd_pd(va1, vb1, acc1);

        __m256d va2 = _mm256_loadu_pd(a + i + 8);
        __m256d vb2 = _mm256_loadu_pd(b + i + 8);
        acc2 = _mm256_fmadd_pd(va2, vb2, acc2);

        __m256d va3 = _mm256_loadu_pd(a + i + 12);
        __m256d vb3 = _mm256_loadu_pd(b + i + 12);
        acc3 = _mm256_fmadd_pd(va3, vb3, acc3);
    }

    /* Об'єднання векторних акумуляторів */
    __m256d sum_acc = _mm256_add_pd(_mm256_add_pd(acc0, acc1),
                                     _mm256_add_pd(acc2, acc3));

    /* Горизонтальне додавання 4 елементів у регістрі ymm */
    __m128d hi128 = _mm256_extractf128_pd(sum_acc, 1);
    __m128d lo128 = _mm256_castpd256_pd128(sum_acc);
    __m128d sum128 = _mm_add_pd(lo128, hi128);
    __m128d hi64 = _mm_unpackhi_pd(sum128, sum128);
    double total = _mm_cvtsd_f64(_mm_add_sd(sum128, hi64));

    /* Дообчислення залишку масиву */
    for (; i < n; ++i) {
        total = fma(a[i], b[i], total);
    }

    return total;
}
