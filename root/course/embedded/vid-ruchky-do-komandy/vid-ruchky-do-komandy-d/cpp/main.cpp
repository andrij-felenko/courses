#include <cmath>
#include <algorithm>
#include <numbers>

namespace flight_control {

struct StickGeometry {
    float raw_min{1000.0f};
    float raw_center{1500.0f};
    float raw_max{2000.0f};
    float deadband_center{0.04f}; // 4% мертва зона в центрі
    float deadband_end{0.02f};    // 2% мертва зона на упорі
};

struct ActualRates {
    float center_rate{200.0f};    // deg/s навколо нуля
    float max_rate{850.0f};       // deg/s на крайньому упорі
    float expo{0.55f};            // коефіцієнт пом'якшення [0..1]
};

class AxisProcessor {
public:
    constexpr AxisProcessor(StickGeometry geom, ActualRates rates, float cutoff_hz = 45.0f) noexcept
        : geom_{geom}, rates_{rates}, cutoff_hz_{cutoff_hz} {}

    [[nodiscard]] float process(float raw_input, float dt_sec) noexcept {
        const float norm = normalize(raw_input);
        const float active_stick = apply_deadband(norm);
        const float target_rate = calculate_rate(active_stick);
        return apply_pt1_filter(target_rate, dt_sec);
    }

    void reset() noexcept { filter_state_ = 0.0f; }
    [[nodiscard]] float current_rate() const noexcept { return filter_state_; }

private:
    [[nodiscard]] float normalize(float raw) const noexcept {
        float norm = 0.0f;
        if (raw >= geom_.raw_center) {
            const float span = geom_.raw_max - geom_.raw_center;
            norm = (span > 1e-3f) ? (raw - geom_.raw_center) / span : 0.0f;
        } else {
            const float span = geom_.raw_center - geom_.raw_min;
            norm = (span > 1e-3f) ? (raw - geom_.raw_center) / span : 0.0f;
        }
        return std::clamp(norm, -1.0f, 1.0f);
    }

    [[nodiscard]] float apply_deadband(float norm) const noexcept {
        const float abs_x = std::abs(norm);
        if (abs_x <= geom_.deadband_center) {
            return 0.0f;
        }
        if (abs_x >= (1.0f - geom_.deadband_end)) {
            return std::copysign(1.0f, norm);
        }
        const float range = 1.0f - geom_.deadband_center - geom_.deadband_end;
        if (range < 1e-3f) {
            return 0.0f;
        }
        return std::copysign((abs_x - geom_.deadband_center) / range, norm);
    }

    [[nodiscard]] float calculate_rate(float stick_pos) const noexcept {
        const float x = std::abs(stick_pos);
        const float x5 = x * x * x * x * x;
        const float curve = x * (1.0f - rates_.expo) + x5 * rates_.expo;
        const float rate = x * rates_.center_rate + (rates_.max_rate - rates_.center_rate) * curve;
        return std::copysign(rate, stick_pos);
    }

    [[nodiscard]] float apply_pt1_filter(float target, float dt_sec) noexcept {
        if (dt_sec <= 0.0f || cutoff_hz_ <= 0.0f) {
            filter_state_ = target;
            return filter_state_;
        }
        constexpr float two_pi = 2.0f * std::numbers::pi_v<float>;
        const float rc = 1.0f / (two_pi * cutoff_hz_);
        const float alpha = std::clamp(dt_sec / (rc + dt_sec), 0.0f, 1.0f);
        filter_state_ += alpha * (target - filter_state_);
        return filter_state_;
    }

    StickGeometry geom_;
    ActualRates rates_;
    float cutoff_hz_{45.0f};
    float filter_state_{0.0f};
};

} // namespace flight_control
