#include <vector>
#include <span>
#include <cmath>
#include <expected>
#include <algorithm>

struct SparseElement {
    size_t index;
    float value;
};

class SparseCosineMetric {
public:
    static std::expected<float, MetricError> compute(
        std::span<const SparseElement> u,
        std::span<const SparseElement> v
    ) noexcept {
        if (u.empty() || v.empty()) {
            return std::unexpected(MetricError::EmptyVector);
        }

        float sq_u = 0.0f;
        for (const auto& elem : u) sq_u += elem.value * elem.value;

        float sq_v = 0.0f;
        for (const auto& elem : v) sq_v += elem.value * elem.value;

        float dot = 0.0f;
        size_t i = 0, j = 0;

        while (i < u.size() && j < v.size()) {
            if (u[i].index == v[j].index) {
                dot += u[i].value * v[j].value;
                ++i;
                ++j;
            } else if (u[i].index < v[j].index) {
                ++i;
            } else {
                ++j;
            }
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
