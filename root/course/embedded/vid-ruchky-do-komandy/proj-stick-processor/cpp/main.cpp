#include <cmath>
#include <algorithm>
#include <span>
#include <array>
#include <numbers>

namespace flight_control {

struct StickCalibration {
    float raw_min{1000.0f};
    float raw_center{1500.0f};
    float raw_max{2000.0f};
    float center_deadband{0.04f}; // 4% мертва зона в нулі
    float end_deadband{0.02f};    // 2% мертва зона на упорах
};

struct ActualRatesConfig {
    float center_rate{200.0f};    // Чутливість біля нуля (deg/s)
    float max_rate{850.0f};       // Максимальна кутова швидкість (deg/s)
    float expo{0.55f};            // Кривина переходу [0.0 .. 1.0]
};

class RcSmoothingFilter {
public:
    constexpr explicit RcSmoothingFilter(float cutoff_hz = 45.0f) noexcept
        : cutoff_hz_{cutoff_hz} {}

    [[nodiscard]] float process(float target, float dt_seconds) noexcept {
        if (dt_seconds <= 0.0f || cutoff_hz_ <= 0.0f) {
            state_ = target;
            return state_;
        }
        constexpr float two_pi = 2.0f * std::numbers::pi_v<float>;
        const float rc = 1.0f / (two_pi * cutoff_hz_);
        const float alpha = std::clamp(dt_seconds / (rc + dt_seconds), 0.0f, 1.0f);

        state_ += alpha * (target - state_);
        return state_;
    }

    void reset(float initial_value = 0.0f) noexcept {
        state_ = initial_value;
    }

    [[nodiscard]] float state() const noexcept { return state_; }
    void set_cutoff(float hz) noexcept { cutoff_hz_ = (hz > 0.0f) ? hz : 45.0f; }

private:
    float state_{0.0f};
    float cutoff_hz_{45.0f};
};

class StickAxisProcessor {
public:
    constexpr StickAxisProcessor(StickCalibration calib, ActualRatesConfig rates, float cutoff_hz = 45.0f) noexcept
        : calib_{calib}, rates_{rates}, filter_{cutoff_hz} {}

    [[nodiscard]] float process(float raw_input, float dt_seconds) noexcept {
        const float norm = normalize(raw_input);
        const float active_stick = apply_deadband(norm);
        const float target_rate = calculate_actual_rate(active_stick);
        return filter_.process(target_rate, dt_seconds);
    }

    void reset() noexcept {
        filter_.reset(0.0f);
    }

    [[nodiscard]] const StickCalibration& calibration() const noexcept { return calib_; }
    [[nodiscard]] const ActualRatesConfig& rates() const noexcept { return rates_; }
    void set_rates(const ActualRatesConfig& r) noexcept { rates_ = r; }
    void set_cutoff(float hz) noexcept { filter_.set_cutoff(hz); }

private:
    [[nodiscard]] float normalize(float raw) const noexcept {
        float norm = 0.0f;
        if (raw >= calib_.raw_center) {
            const float span = calib_.raw_max - calib_.raw_center;
            if (span > 1e-3f) {
                norm = (raw - calib_.raw_center) / span;
            }
        } else {
            const float span = calib_.raw_center - calib_.raw_min;
            if (span > 1e-3f) {
                norm = (raw - calib_.raw_center) / span;
            }
        }
        return std::clamp(norm, -1.0f, 1.0f);
    }

    [[nodiscard]] float apply_deadband(float norm) const noexcept {
        const float sign = (norm >= 0.0f) ? 1.0f : -1.0f;
        const float abs_val = std::abs(norm);

        if (abs_val <= calib_.center_deadband) {
            return 0.0f;
        }
        if (abs_val >= (1.0f - calib_.end_deadband)) {
            return sign * 1.0f;
        }

        const float active_range = 1.0f - calib_.center_deadband - calib_.end_deadband;
        if (active_range < 1e-3f) {
            return 0.0f;
        }
        return sign * ((abs_val - calib_.center_deadband) / active_range);
    }

    [[nodiscard]] float calculate_actual_rate(float stick_pos) const noexcept {
        const float sign = (stick_pos >= 0.0f) ? 1.0f : -1.0f;
        const float x = std::abs(stick_pos);

        const float x5 = x * x * x * x * x;
        const float curve = x * (1.0f - rates_.expo) + x5 * rates_.expo;

        const float center_part = x * rates_.center_rate;
        const float max_part = (rates_.max_rate - rates_.center_rate) * curve;
        return sign * (center_part + max_part);
    }

    StickCalibration calib_;
    ActualRatesConfig rates_;
    RcSmoothingFilter filter_;
};

} // namespace flight_control
