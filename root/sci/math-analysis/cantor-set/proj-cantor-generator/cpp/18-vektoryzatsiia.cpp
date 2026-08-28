#include <immintrin.h>
#include <span>

namespace math::fractals {

void scan_avx512(std::span<const double> points, std::span<uint8_t> results, std::size_t depth) {
    const __m512d v_three = _mm512_set1_pd(3.0);
    const __m512d v_one   = _mm512_set1_pd(1.0);

    for (std::size_t i = 0; i + 8 <= points.size(); i += 8) {
        __m512d v_curr = _mm512_loadu_pd(&points[i]);
        __m512d v_floor = _mm512_floor_pd(_mm512_mul_pd(v_curr, v_three));
        __mmask8 m_is_one = _mm512_cmpeq_pd_mask(v_floor, v_one);
        results[i] = m_is_one ? 0 : 1;
    }
}

} // namespace math::fractals
