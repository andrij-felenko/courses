#include <immintrin.h>
#include <cmath>
#include <span>
#include <expected>
#include <algorithm>

class SimdCosineMetric {
private:
    static inline float hsum256(__m256 v) noexcept {
        __m128 vlow  = _mm256_castps256_ps128(v);
        __m128 vhigh = _mm256_extractf128_ps(v, 1);
        vlow  = _mm_add_ps(vlow, vhigh);
        __m128 shuf = _mm_movehdup_ps(vlow);
        vlow  = _mm_add_ps(vlow, shuf);
        shuf  = _mm_movehl_ps(shuf, vlow);
        vlow  = _mm_add_ss(vlow, shuf);
        return _mm_cvtss_f32(vlow);
    }

public:
    static std::expected<float, MetricError> compute(std::span<const float> u, std::span<const float> v) noexcept {
        if (u.empty() || v.empty()) return std::unexpected(MetricError::EmptyVector);
        if (u.size() != v.size()) return std::unexpected(MetricError::SizeMismatch);

        const size_t n = u.size();
        const float* p_u = u.data();
        const float* p_v = v.data();

        __m256 v_dot  = _mm256_setzero_ps();
        __m256 v_sq_u = _mm256_setzero_ps();
        __m256 v_sq_v = _mm256_setzero_ps();

        size_t i = 0;
        for (; i + 7 < n; i += 8) {
            __m256 u_vec = _mm256_loadu_ps(p_u + i);
            __m256 v_vec = _mm256_loadu_ps(p_v + i);

            v_dot  = _mm256_fmadd_ps(u_vec, v_vec, v_dot);
            v_sq_u = _mm256_fmadd_ps(u_vec, u_vec, v_sq_u);
            v_sq_v = _mm256_fmadd_ps(v_vec, v_vec, v_sq_v);
        }

        float dot  = hsum256(v_dot);
        float sq_u = hsum256(v_sq_u);
        float sq_v = hsum256(v_sq_v);

        for (; i < n; ++i) {
            dot  += p_u[i] * p_u[i];
            sq_u += p_u[i] * p_u[i];
            sq_v += p_v[i] * p_v[i];
        }

        constexpr float eps = 1e-12f;
        if (sq_u < eps || sq_v < eps) {
            return std::unexpected(MetricError::ZeroVectorNorm);
        }

        const float norm_prod = std::sqrt(sq_u) * std::sqrt(sq_v);
        const float cos_sim = std::clamp(dot / norm_prod, -1.0f, 1.0f);

        return 1.0f - cos_sim;
    }
};
