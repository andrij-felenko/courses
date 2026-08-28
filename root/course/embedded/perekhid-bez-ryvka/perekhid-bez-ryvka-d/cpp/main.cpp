#include <algorithm>
#include <concepts>
#include <cstdint>

struct PidConfig {
    float kp{0.0f};
    float ki{0.0f};
    float kd{0.0f};
    float kff{0.0f};
    float out_min{-1.0f};
    float out_max{1.0f};
    float i_min{-1.0f};
    float i_max{1.0f};
    float slew_rate_max{0.0f}; // од/с, 0 = вимкнено
};

class BumplessPidController {
public:
    constexpr explicit BumplessPidController(const PidConfig& config) noexcept
        : cfg_{config} {}

    void set_target(float target) noexcept {
        target_setpoint_ = target;
    }

    // Безривкове захоплення керування
    void handover(float current_measurement, float target_setpoint,
                  float prev_actuator_output) noexcept {
        current_setpoint_ = current_measurement;
        target_setpoint_ = target_setpoint;
        prev_measurement_ = current_measurement;

        const float error = current_setpoint_ - current_measurement;
        const float p_term = cfg_.kp * error;
        const float ff_term = cfg_.kff * current_setpoint_;

        const float needed_i = prev_actuator_output - p_term - ff_term;
        integral_ = std::clamp(needed_i, cfg_.i_min, cfg_.i_max);

        last_output_ = prev_actuator_output;
        is_initialized_ = true;
    }

    // Періодичний крок
    [[nodiscard]] float update(float measurement, float dt) noexcept {
        if (!is_initialized_ || dt <= 0.0f) {
            return last_output_;
        }

        // Ремпінг уставки
        if (cfg_.slew_rate_max > 0.0f) {
            const float max_step = cfg_.slew_rate_max * dt;
            const float delta = target_setpoint_ - current_setpoint_;
            if (delta > max_step) {
                current_setpoint_ += max_step;
            } else if (delta < -max_step) {
                current_setpoint_ -= max_step;
            } else {
                current_setpoint_ = target_setpoint_;
            }
        } else {
            current_setpoint_ = target_setpoint_;
        }

        const float error = current_setpoint_ - measurement;
        const float p_term = cfg_.kp * error;

        const float d_meas = (measurement - prev_measurement_) / dt;
        prev_measurement_ = measurement;
        const float d_term = -cfg_.kd * d_meas;

        const float ff_term = cfg_.kff * current_setpoint_;
        const float candidate_i = integral_ + cfg_.ki * error * dt;
        const float u_raw = p_term + candidate_i + d_term + ff_term;

        // Clamping анти-віндап
        const bool sat_high = (u_raw > cfg_.out_max) && (error > 0.0f);
        const bool sat_low  = (u_raw < cfg_.out_min) && (error < 0.0f);
        if (!sat_high && !sat_low) {
            integral_ = std::clamp(candidate_i, cfg_.i_min, cfg_.i_max);
        }

        last_output_ = std::clamp(u_raw, cfg_.out_min, cfg_.out_max);
        return last_output_;
    }

    void reset() noexcept {
        integral_ = 0.0f;
        prev_measurement_ = 0.0f;
        target_setpoint_ = 0.0f;
        current_setpoint_ = 0.0f;
        last_output_ = 0.0f;
        is_initialized_ = false;
    }

    [[nodiscard]] float last_output() const noexcept { return last_output_; }
    [[nodiscard]] float current_setpoint() const noexcept { return current_setpoint_; }
    [[nodiscard]] float integral() const noexcept { return integral_; }

private:
    PidConfig cfg_{};
    float integral_{0.0f};
    float prev_measurement_{0.0f};
    float target_setpoint_{0.0f};
    float current_setpoint_{0.0f};
    float last_output_{0.0f};
    bool is_initialized_{false};
};
