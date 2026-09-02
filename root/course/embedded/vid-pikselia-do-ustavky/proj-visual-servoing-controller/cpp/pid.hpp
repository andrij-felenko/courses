#pragma once

#include <algorithm>
#include <chrono>
#include <cmath>

#include "tracker.hpp"

namespace servo {

/* ПІД контуру супроводу з трьома поправками під зашумлений вхід від
 * нейромережі: похідна за вимірюванням, умовне інтегрування, віднімання
 * зони нечутливості (а не обнулення похибки — інакше на краю зони вихід
 * стрибав би на kp·deadband). */
class ServoingPid {
public:
    struct Config {
        float kp{1.8f};
        float ki{0.1f};
        float kd{0.15f};
        float max_output{1.0f};
        float max_integral{0.3f};
        float deadband{0.008f};
    };

    constexpr explicit ServoingPid(Config cfg) noexcept : cfg_{cfg} {}

    float update(float setpoint, float measurement, Seconds dt) noexcept {
        const float h = dt.count();
        if (!(h > 0.0f) || !std::isfinite(measurement)) {
            return 0.0f;
        }

        float error = setpoint - measurement;
        if (std::abs(error) < cfg_.deadband) {
            error = 0.0f;
        } else {
            error -= std::copysign(cfg_.deadband, error);
        }

        const float p_term = cfg_.kp * error;

        const float integral_before = integral_;
        integral_ = std::clamp(integral_ + error * h, -cfg_.max_integral, cfg_.max_integral);
        const float i_term = cfg_.ki * integral_;

        float d_term = 0.0f;
        if (primed_) {
            d_term = -cfg_.kd * (measurement - prev_meas_) / h;
        } else {
            primed_ = true;
        }
        prev_meas_ = measurement;

        const float raw = p_term + i_term + d_term;
        if (std::abs(raw) > cfg_.max_output &&
            ((raw > 0.0f && error > 0.0f) || (raw < 0.0f && error < 0.0f))) {
            /* Привід уже в упорі — інтеграл далі не росте. */
            integral_ = integral_before;
        }
        return std::clamp(raw, -cfg_.max_output, cfg_.max_output);
    }

    constexpr void reset() noexcept {
        integral_ = 0.0f;
        prev_meas_ = 0.0f;
        primed_ = false;
    }

private:
    Config cfg_;
    float integral_{0.0f};
    float prev_meas_{0.0f};
    bool primed_{false};
};

}  // namespace servo
