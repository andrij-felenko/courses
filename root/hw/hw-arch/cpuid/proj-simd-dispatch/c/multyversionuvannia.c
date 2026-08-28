#include <stddef.h>
#include <immintrin.h>

// Скалярне ядро: працює на будь-якому процесорі x86
float vec_sum_scalar(const float* data, size_t count) {
    float sum = 0.0f;
    for (size_t i = 0; i < count; ++i) {
        sum += data[i];
    }
    return sum;
}

// AVX2 ядро: обробка по 8 елементів float за один такт
__attribute__((target("avx2,fma")))
float vec_sum_avx2(const float* data, size_t count) {
    __m256 acc = _mm256_setzero_ps();
    size_t i = 0;
    for (; i + 8 <= count; i += 8) {
        __m256 v = _mm256_loadu_ps(data + i);
        acc = _mm256_add_ps(acc, v);
    }
    // Горизонтальне згортання 8 елементів регістру YMM
    __m128 lo = _mm256_castps256_ps128(acc);
    __m128 hi = _mm256_extractf128_ps(acc, 1);
    __m128 sum128 = _mm_add_ps(lo, hi);
    sum128 = _mm_hadd_ps(sum128, sum128);
    sum128 = _mm_hadd_ps(sum128, sum128);
    float total = _mm_cvtss_f32(sum128);

    // Обробка залишкових елементів
    for (; i < count; ++i) {
        total += data[i];
    }
    return total;
}

typedef float (*vec_sum_fn)(const float*, size_t);
