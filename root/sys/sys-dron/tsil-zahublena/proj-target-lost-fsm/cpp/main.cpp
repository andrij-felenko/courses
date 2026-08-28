#include <array>
#include <cmath>
#include <cstdint>
#include <numbers>
#include <optional>
#include <span>

namespace drone::tracking {

inline constexpr std::size_t kReIdEmbeddingDim = 128;

enum class TrackerState : uint8_t {
    Tracking = 0,
    Coast,
    Search,
    Disengaged
};

struct Vec3 {
    float x{0.0F};
    float y{0.0F};
    float z{0.0F};

    constexpr Vec3& operator+=(const Vec3& rhs) noexcept {
        x += rhs.x;
        y += rhs.y;
        z += rhs.z;
        return *this;
    }
};

struct GimbalAngles {
    float pan{0.0F};
    float tilt{0.0F};
};

struct Detection {
    Vec3 pos{};
    Vec3 vel{};
    std::array<float, 3> cov_pos{1.0F, 1.0F, 1.0F};
    std::array<float, kReIdEmbeddingDim> descriptor{};
};

struct TrackerConfig {
    float t_coast_limit{1.5F};
    float t_search_limit{5.0F};
    float spiral_a{0.05F};
    float spiral_b{0.02F};
    float spiral_omega{2.5F};
    float gate_threshold{9.21F};     // 99% квантиль хі-квадрат для 3 DoF
    float reid_threshold{0.65F};
    float process_noise{2.0F};
    float max_gimbal_rate{3.14F};
};

class TargetLostFsm {
public:
    explicit TargetLostFsm(const TrackerConfig& config) noexcept
        : config_{config} {}

    void update(const std::optional<Detection>& det, float dt) noexcept {
        const bool reacquired = try_reacquire(det);

        switch (state_) {
        case TrackerState::Tracking:
            if (reacquired) {
                state_timer_ = 0.0F;
            } else {
                state_ = TrackerState::Coast;
                state_timer_ = 0.0F;
            }
            break;

        case TrackerState::Coast:
            if (reacquired) {
                state_ = TrackerState::Tracking;
                state_timer_ = 0.0F;
            } else {
                state_timer_ += dt;
                extrapolate_target(dt, 1.0F);

                if (state_timer_ >= config_.t_coast_limit) {
                    state_ = TrackerState::Search;
                    state_timer_ = 0.0F;
                    search_theta_ = 0.0F;
                }
            }
            break;

        case TrackerState::Search:
            if (reacquired) {
                state_ = TrackerState::Tracking;
                state_timer_ = 0.0F;
            } else {
                state_timer_ += dt;
                generate_search_pattern(dt);
                extrapolate_target(dt, 0.5F);

                if (state_timer_ >= config_.t_search_limit) {
                    state_ = TrackerState::Disengaged;
                    state_timer_ = 0.0F;
                }
            }
            break;

        case TrackerState::Disengaged:
            if (reacquired) {
                state_ = TrackerState::Tracking;
                state_timer_ = 0.0F;
            }
            break;
        }
    }

    [[nodiscard]] TrackerState state() const noexcept { return state_; }
    [[nodiscard]] Vec3 estimated_position() const noexcept { return est_pos_; }
    [[nodiscard]] GimbalAngles gimbal_command() const noexcept { return gimbal_cmd_; }

private:
    [[nodiscard]] static float compute_reid_similarity(
        std::span<const float, kReIdEmbeddingDim> a,
        std::span<const float, kReIdEmbeddingDim> b) noexcept {
        float dot = 0.0F;
        float norm_a = 0.0F;
        float norm_b = 0.0F;
        for (std::size_t i = 0; i < kReIdEmbeddingDim; ++i) {
            dot += a[i] * b[i];
            norm_a += a[i] * a[i];
            norm_b += b[i] * b[i];
        }
        const float denom = std::sqrt(norm_a) * std::sqrt(norm_b);
        return (denom > 1e-6F) ? (dot / denom) : 0.0F;
    }

    [[nodiscard]] bool check_spatial_gate(const Vec3& meas) const noexcept {
        const float dx = meas.x - est_pos_.x;
        const float dy = meas.y - est_pos_.y;
        const float dz = meas.z - est_pos_.z;

        const float sx = std::max(cov_pos_[0], 1e-4F);
        const float sy = std::max(cov_pos_[1], 1e-4F);
        const float sz = std::max(cov_pos_[2], 1e-4F);

        const float dist_sq = (dx * dx) / sx + (dy * dy) / sy + (dz * dz) / sz;
        return dist_sq <= config_.gate_threshold;
    }

    bool try_reacquire(const std::optional<Detection>& det) noexcept {
        if (!det.has_value()) {
            return false;
        }

        if (state_ == TrackerState::Coast || state_ == TrackerState::Search) {
            if (!check_spatial_gate(det->pos)) {
                return false;
            }
            const float sim = compute_reid_similarity(det->descriptor, ref_descriptor_);
            if (sim < config_.reid_threshold) {
                return false;
            }
        }

        est_pos_ = det->pos;
        est_vel_ = det->vel;
        cov_pos_ = det->cov_pos;
        /* Експоненційне згладжування дескриптора */
        for (std::size_t i = 0; i < kReIdEmbeddingDim; ++i) {
            ref_descriptor_[i] = 0.9F * ref_descriptor_[i] + 0.1F * det->descriptor[i];
        }
        return true;
    }

    void extrapolate_target(float dt, float vel_scale) noexcept {
        est_pos_.x += est_vel_.x * dt * vel_scale;
        est_pos_.y += est_vel_.y * dt * vel_scale;
        est_pos_.z += est_vel_.z * dt * vel_scale;

        cov_pos_[0] += config_.process_noise * dt;
        cov_pos_[1] += config_.process_noise * dt;
        cov_pos_[2] += config_.process_noise * dt;
    }

    void generate_search_pattern(float dt) noexcept {
        search_theta_ += config_.spiral_omega * dt;
        const float r = config_.spiral_a + config_.spiral_b * search_theta_;
        gimbal_cmd_.pan = r * std::cos(search_theta_);
        gimbal_cmd_.tilt = r * std::sin(search_theta_);
    }

    TrackerConfig config_{};
    TrackerState state_{TrackerState::Disengaged};
    Vec3 est_pos_{};
    Vec3 est_vel_{};
    std::array<float, 3> cov_pos_{1.0F, 1.0F, 1.0F};
    std::array<float, kReIdEmbeddingDim> ref_descriptor_{};
    float state_timer_{0.0F};
    float search_theta_{0.0F};
    GimbalAngles gimbal_cmd_{};
};

} // namespace drone::tracking
