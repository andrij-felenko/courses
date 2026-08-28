#include <cmath>
#include <span>
#include <expected>
#include <algorithm>

enum class MetricError {
    EmptyVector,
    SizeMismatch,
    ZeroVectorNorm
};

class CosineMetric {
public:
    static std::expected<float, MetricError> compute(std::span<const float> u, std::span<const float> v) {
        if (u.empty() || v.empty()) {
            return std::unexpected(MetricError::EmptyVector);
        }
        if (u.size() != v.size()) {
            return std::unexpected(MetricError::SizeMismatch);
        }

        float dot = 0.0f;
        float sq_u = 0.0f;
        float sq_v = 0.0f;

        const size_t n = u.size();
        size_t i = 0;

        // Ідіоматичний C++20 прохід з розгортанням
        for (; i + 3 < n; i += 4) {
            float u0 = u[i],   u1 = u[i+1], u2 = u[i+2], u3 = u[i+3];
            float v0 = v[i],   v1 = v[i+1], v2 = v[i+2], v3 = v[i+3];

            dot  += u0 * v0 + u1 * v1 + u2 * v2 + u3 * v3;
            sq_u += u0 * u0 + u1 * u1 + u2 * u2 + u3 * u3;
            sq_v += v0 * v0 + v1 * v1 + v2 * v2 + v3 * v3;
        }

        for (; i < n; ++i) {
            dot  += u[i] * v[i];
            sq_u += u[i] * u[i];
            sq_v += v[i] * v[i];
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
