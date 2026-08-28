#include <span>
#include <cstddef>
#include <numeric>
#include <immintrin.h>

struct VectorKernels {
    static float sum_scalar(std::span<const float> data) noexcept {
        return std::accumulate(data.begin(), data.end(), 0.0f);
    }

    __attribute__((target("avx2,fma")))
    static float sum_avx2(std::span<const float> data) noexcept {
        __m256 acc = _mm256_setzero_ps();
        const std::size_t count = data.size();
        const float* ptr = data.data();
        std::size_t i = 0;

        for (; i + 8 <= count; i += 8) {
            __m256 v = _mm256_loadu_ps(ptr + i);
            acc = _mm256_add_ps(acc, v);
        }

        __m128 lo = _mm256_castps256_ps128(acc);
        __m128 hi = _mm256_extractf128_ps(acc, 1);
        __m128 sum128 = _mm_add_ps(lo, hi);
        sum128 = _mm_hadd_ps(sum128, sum128);
        sum128 = _mm_hadd_ps(sum128, sum128);
        float total = _mm_cvtss_f32(sum128);

        for (; i < count; ++i) {
            total += ptr[i];
        }
        return total;
    }
};

using VecSumFn = float (*)(std::span<const float>) noexcept;
