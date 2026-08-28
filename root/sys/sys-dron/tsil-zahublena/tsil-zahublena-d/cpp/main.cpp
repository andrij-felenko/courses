#include <array>
#include <cmath>
#include <cstdint>
#include <optional>
#include <span>

namespace drone::tracking {

inline constexpr std::size_t kEmbeddingDim = 128;

struct Point3D {
    float x{0.0F};
    float y{0.0F};
    float z{0.0F};
};

struct TargetCandidate {
    Point3D pos{};
    std::array<float, 3> cov{0.1F, 0.1F, 0.1F};
    std::array<float, kEmbeddingDim> descriptor{};
};

struct GatingConfig {
    float mahalanobis_threshold{9.21F}; // 99% квантиль хі-квадрат (3 DoF)
    float appearance_threshold{0.65F};  // Поріг косинусної близькості
    float weight_spatial{0.4F};
    float weight_appearance{0.6F};
};

class CandidateValidator {
public:
    explicit CandidateValidator(const GatingConfig& config) noexcept
        : config_{config} {}

    [[nodiscard]] std::optional<float> evaluate_candidate(
        const TargetCandidate& cand,
        const Point3D& pred_pos,
        std::span<const float, 3> pred_cov,
        std::span<const float, kEmbeddingDim> ref_descriptor) const noexcept
    {
        const float dx = cand.pos.x - pred_pos.x;
        const float dy = cand.pos.y - pred_pos.y;
        const float dz = cand.pos.z - pred_pos.z;

        const float var_x = std::max(pred_cov[0] + cand.cov[0], 1e-4F);
        const float var_y = std::max(pred_cov[1] + cand.cov[1], 1e-4F);
        const float var_z = std::max(pred_cov[2] + cand.cov[2], 1e-4F);

        const float d_mahalanobis_sq = (dx * dx) / var_x + (dy * dy) / var_y + (dz * dz) / var_z;
        if (d_mahalanobis_sq > config_.mahalanobis_threshold) {
            return std::nullopt;
        }

        const float app_sim = compute_cosine_similarity(cand.descriptor, ref_descriptor);
        if (app_sim < config_.appearance_threshold) {
            return std::nullopt;
        }

        const float spatial_score = std::max(0.0F, 1.0F - (d_mahalanobis_sq / config_.mahalanobis_threshold));
        const float total_score = config_.weight_spatial * spatial_score + config_.weight_appearance * app_sim;

        return total_score;
    }

private:
    [[nodiscard]] static float compute_cosine_similarity(
        std::span<const float, kEmbeddingDim> a,
        std::span<const float, kEmbeddingDim> b) noexcept
    {
        float dot = 0.0F;
        float norm_a = 0.0F;
        float norm_b = 0.0F;
        for (std::size_t i = 0; i < kEmbeddingDim; ++i) {
            dot += a[i] * b[i];
            norm_a += a[i] * a[i];
            norm_b += b[i] * b[i];
        }
        const float denom = std::sqrt(norm_a) * std::sqrt(norm_b);
        return (denom > 1e-6F) ? (dot / denom) : 0.0F;
    }

    GatingConfig config_{};
};

} // namespace drone::tracking
