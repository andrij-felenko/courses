#include <immintrin.h>
#include <span>

void transpose_8x8_aos_to_soa(std::span<const float, 32> aos_src,
                              std::span<float, 8> soa_x,
                              std::span<float, 8> soa_y,
                              std::span<float, 8> soa_z) noexcept
{
    __m256 r0 = _mm256_loadu_ps(aos_src.data() + 0);
    __m256 r1 = _mm256_loadu_ps(aos_src.data() + 8);
    __m256 r2 = _mm256_loadu_ps(aos_src.data() + 16);
    __m256 r3 = _mm256_loadu_ps(aos_src.data() + 24);

    __m256 t0 = _mm256_unpacklo_ps(r0, r1);
    __m256 t1 = _mm256_unpackhi_ps(r0, r1);
    __m256 t2 = _mm256_unpacklo_ps(r2, r3);
    __m256 t3 = _mm256_unpackhi_ps(r2, r3);

    __m256 v_x = _mm256_shuffle_ps(t0, t2, _MM_SHUFFLE(2, 0, 2, 0));
    __m256 v_y = _mm256_shuffle_ps(t0, t2, _MM_SHUFFLE(3, 1, 3, 1));
    __m256 v_z = _mm256_shuffle_ps(t1, t3, _MM_SHUFFLE(2, 0, 2, 0));

    _mm256_storeu_ps(soa_x.data(), v_x);
    _mm256_storeu_ps(soa_y.data(), v_y);
    _mm256_storeu_ps(soa_z.data(), v_z);
}
