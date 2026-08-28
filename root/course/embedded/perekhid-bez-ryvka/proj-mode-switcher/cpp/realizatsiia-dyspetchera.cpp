#include <iostream>
#include <algorithm>
#include <concepts>
#include <cstdint>

enum class FlightMode : uint8_t {
    Manual = 0,
    AltHold,
    AutoMission
};

struct PidConfig {
    float kp{0.0f};
    float ki{0.0f};
    float kd{0.0f};
    float kff{0.0f};
    float out_min{0.0f};
    float out_max{1.0f};
    float i_min{0.0f};
    float i_max{0.9f};
    float slew_rate_max{0.0f};
};

class BumplessPidController {
public:
    constexpr explicit BumplessPidController(const PidConfig& config) noexcept
        : cfg_{config} {}

    void handover(float current_measurement, float target_setpoint,
                  float prev_actuator_output) noexcept {
        current_setpoint_ = current_measurement;
        target_setpoint_ = target_setpoint;
        prev_measurement_ = current_measurement;

        const float err = current_setpoint_ - current_measurement;
        const float p_term = cfg_.kp * err;
        const float ff_term = cfg_.kff * current_setpoint_;

        const float needed_i = prev_actuator_output - p_term - ff_term;
        integral_ = std::clamp(needed_i, cfg_.i_min, cfg_.i_max);
        last_output_ = prev_actuator_output;
        is_initialized_ = true;
    }

    [[nodiscard]] float update(float measurement, float dt) noexcept {
        if (!is_initialized_ || dt <= 0.0f) return last_output_;

        if (cfg_.slew_rate_max > 0.0f) {
            const float max_step = cfg_.slew_rate_max * dt;
            const float d = target_setpoint_ - current_setpoint_;
            if (d > max_step) current_setpoint_ += max_step;
            else if (d < -max_step) current_setpoint_ -= max_step;
            else current_setpoint_ = target_setpoint_;
        } else {
            current_setpoint_ = target_setpoint_;
        }

        const float err = current_setpoint_ - measurement;
        const float p_term = cfg_.kp * err;

        const float d_meas = (measurement - prev_measurement_) / dt;
        prev_measurement_ = measurement;
        const float d_term = -cfg_.kd * d_meas;

        const float ff_term = cfg_.kff * current_setpoint_;
        const float cand_i = integral_ + cfg_.ki * err * dt;
        const float u_raw = p_term + cand_i + d_term + ff_term;

        const bool sat_h = (u_raw > cfg_.out_max) && (err > 0.0f);
        const bool sat_l = (u_raw < cfg_.out_min) && (err < 0.0f);
        if (!sat_h && !sat_l) {
            integral_ = std::clamp(cand_i, cfg_.i_min, cfg_.i_max);
        }

        last_output_ = std::clamp(u_raw, cfg_.out_min, cfg_.out_max);
        return last_output_;
    }

    [[nodiscard]] float last_output() const noexcept { return last_output_; }

private:
    PidConfig cfg_{};
    float integral_{0.0f};
    float prev_measurement_{0.0f};
    float target_setpoint_{0.0f};
    float current_setpoint_{0.0f};
    float last_output_{0.0f};
    bool is_initialized_{false};
};

class FlightManager {
public:
    FlightManager()
        : alt_hold_pid_{PidConfig{
              .kp = 0.08f, .ki = 0.04f, .kd = 0.02f, .kff = 0.0f,
              .out_min = 0.0f, .out_max = 1.0f,
              .i_min = 0.0f, .i_max = 0.9f,
              .slew_rate_max = 2.0f
          }},
          auto_mission_pid_{PidConfig{
              .kp = 0.12f, .ki = 0.05f, .kd = 0.03f, .kff = 0.0f,
              .out_min = 0.0f, .out_max = 1.0f,
              .i_min = 0.0f, .i_max = 0.9f,
              .slew_rate_max = 3.5f
          }} {}

    void switch_mode(FlightMode new_mode, float current_alt, float mission_target_alt) noexcept {
        if (new_mode == current_mode_) return;

        const float prev_out = last_actuator_output_;

        switch (new_mode) {
            case FlightMode::Manual:
                break;
            case FlightMode::AltHold:
                alt_hold_pid_.handover(current_alt, current_alt, prev_out);
                break;
            case FlightMode::AutoMission:
                auto_mission_pid_.handover(current_alt, mission_target_alt, prev_out);
                break;
        }

        current_mode_ = new_mode;
    }

    [[nodiscard]] float step(float stick_throttle, float current_alt, float dt) noexcept {
        float out = 0.0f;
        switch (current_mode_) {
            case FlightMode::Manual:
                out = stick_throttle;
                break;
            case FlightMode::AltHold:
                out = alt_hold_pid_.update(current_alt, dt);
                break;
            case FlightMode::AutoMission:
                out = auto_mission_pid_.update(current_alt, dt);
                break;
        }
        last_actuator_output_ = out;
        return out;
    }

    [[nodiscard]] FlightMode current_mode() const noexcept { return current_mode_; }

private:
    FlightMode current_mode_{FlightMode::Manual};
    BumplessPidController alt_hold_pid_;
    BumplessPidController auto_mission_pid_;
    float last_actuator_output_{0.0f};
};
