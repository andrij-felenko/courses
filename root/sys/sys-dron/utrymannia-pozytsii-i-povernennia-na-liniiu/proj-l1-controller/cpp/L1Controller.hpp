// L1Controller.hpp - Модуль L1-навігації мовою C++ (C++20)
#pragma once

#include <cmath>
#include <numbers>
#include <algorithm>
#include <expected>
#include <span>
#include <string_view>

namespace navigation {

inline constexpr float GRAVITY = 9.80665f;
inline constexpr float PI = std::numbers::pi_v<float>;

struct Vector2D {
    float x{0.0f};
    float y{0.0f};

    [[nodiscard]] constexpr Vector2D operator+(const Vector2D& rhs) const noexcept {
        return {x + rhs.x, y + rhs.y};
    }
    [[nodiscard]] constexpr Vector2D operator-(const Vector2D& rhs) const noexcept {
        return {x - rhs.x, y - rhs.y};
    }
    [[nodiscard]] constexpr Vector2D operator*(float scalar) const noexcept {
        return {x * scalar, y * scalar};
    }
    [[nodiscard]] float length() const noexcept {
        return std::hypot(x, y);
    }
    [[nodiscard]] constexpr float dot(const Vector2D& rhs) const noexcept {
        return x * rhs.x + y * rhs.y;
    }
    [[nodiscard]] constexpr float cross(const Vector2D& rhs) const noexcept {
        return x * rhs.y - y * rhs.x;
    }
};

struct L1Params {
    float period_l1{18.0f};
    float damping_ratio{0.7071f};
    float k_i{0.035f};
    float i_limit{25.0f};
    float roll_limit_rad{30.0f * PI / 180.0f};
    float min_l1_dist{15.0f};
    float max_l1_dist{250.0f};
};

struct L1Output {
    float lateral_accel_mps2{0.0f};
    float roll_setpoint_rad{0.0f};
    float cross_track_error_m{0.0f};
    float lookahead_distance_m{0.0f};
};

enum class NavigationError {
    ZeroVelocity,
    DegenerateSegment,
    InvalidRadius
};

class L1Controller {
public:
    explicit constexpr L1Controller(L1Params params = {}) noexcept
        : params_(params) {}

    void resetIntegrator() noexcept {
        integrator_ect_ = 0.0f;
    }

    void setParams(const L1Params& params) noexcept {
        params_ = params;
    }

    [[nodiscard]] const L1Params& getParams() const noexcept {
        return params_;
    }

    [[nodiscard]] std::expected<L1Output, NavigationError> updateLine(
        Vector2D pos,
        Vector2D vel,
        Vector2D wa,
        Vector2D wb,
        float dt) noexcept;

    [[nodiscard]] std::expected<L1Output, NavigationError> updateOrbit(
        Vector2D pos,
        Vector2D vel,
        Vector2D center,
        float radius,
        bool clockwise,
        float dt) noexcept;

private:
    [[nodiscard]] float computeLookaheadDistance(float ground_speed) const noexcept {
        const float l1 = (params_.period_l1 * ground_speed) / (std::numbers::sqrt2_v<float> * PI);
        return std::clamp(l1, params_.min_l1_dist, params_.max_l1_dist);
    }

    [[nodiscard]] float convertAccelToRoll(float lateral_accel) const noexcept {
        const float max_accel = GRAVITY * std::tan(params_.roll_limit_rad);
        const float clamped_accel = std::clamp(lateral_accel, -max_accel, max_accel);
        return std::atan2(clamped_accel, GRAVITY);
    }

    L1Params params_{};
    float integrator_ect_{0.0f};
    float cross_track_error_{0.0f};
};

} // namespace navigation
