// Драйвер сервомеханічного захвату маніпулятора (C++20 / RAII)
#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>
#include <expected>
#include <chrono>

namespace drone::manipulator {

enum class GripperState : uint8_t {
    Idle,
    Closing,
    Holding,
    Opening,
    Fault
};

enum class GripperError : uint8_t {
    None,
    Timeout,
    Overcurrent,
    SlipDetected
};

struct GripperTelemetry {
    GripperState state{GripperState::Idle};
    GripperError error{GripperError::None};
    float current_force_n{0.0F};
    float motor_current_a{0.0F};
    float jaw_position_mm{0.0F};
};

class GripperController {
public:
    struct Config {
        float current_to_force_ratio{45.0F}; // Н / А
        float contact_threshold_a{0.6F};     // А
        float max_safe_current_a{4.5F};      // А
        float kp{0.05F};
        float ki{0.002F};
        float min_holding_duty{0.15F};
        float max_holding_duty{0.90F};
    };

    explicit GripperController(Config config = Config{}) noexcept
        : cfg_{config} {}

    void grip(float target_force_n) noexcept {
        target_force_n_ = target_force_n;
        integral_accum_ = 0.0F;
        state_ = GripperState::Closing;
        error_ = GripperError::None;
        state_elapsed_ms_ = 0;
    }

    void release() noexcept {
        state_ = GripperState::Opening;
        error_ = GripperError::None;
        state_elapsed_ms_ = 0;
    }

    [[nodiscard]] std::expected<float, GripperError> update(
        float current_a, 
        float position_mm, 
        std::chrono::milliseconds dt) noexcept 
    {
        last_current_a_ = current_a;
        last_pos_mm_ = position_mm;
        state_elapsed_ms_ += static_cast<uint32_t>(dt.count());

        if (std::abs(current_a) > cfg_.max_safe_current_a) {
            state_ = GripperState::Fault;
            error_ = GripperError::Overcurrent;
            return std::unexpected(GripperError::Overcurrent);
        }

        float duty_cycle = 0.0F;

        switch (state_) {
            case GripperState::Idle:
                duty_cycle = 0.0F;
                break;

            case GripperState::Closing:
                duty_cycle = 0.35F;
                if (current_a > cfg_.contact_threshold_a) {
                    state_ = GripperState::Holding;
                    integral_accum_ = 0.0F;
                    state_elapsed_ms_ = 0;
                } else if (state_elapsed_ms_ > 3000) {
                    state_ = GripperState::Fault;
                    error_ = GripperError::Timeout;
                    return std::unexpected(GripperError::Timeout);
                }
                break;

            case GripperState::Holding: {
                const float est_force = current_a * cfg_.current_to_force_ratio;
                const float force_err = target_force_n_ - est_force;

                integral_accum_ += force_err * static_cast<float>(dt.count());
                integral_accum_ = std::clamp(integral_accum_, -100.0F, 100.0F);

                duty_cycle = (cfg_.kp * force_err) + (cfg_.ki * integral_accum_);
                duty_cycle = std::clamp(duty_cycle, cfg_.min_holding_duty, cfg_.max_holding_duty);

                // Детектування прослизання вантажу
                if (current_a < (cfg_.contact_threshold_a * 0.4F) && state_elapsed_ms_ > 500) {
                    state_ = GripperState::Fault;
                    error_ = GripperError::SlipDetected;
                    return std::unexpected(GripperError::SlipDetected);
                }
                break;
            }

            case GripperState::Opening:
                duty_cycle = -0.50F;
                if (position_mm <= 1.0F || state_elapsed_ms_ > 2000) {
                    state_ = GripperState::Idle;
                    duty_cycle = 0.0F;
                }
                break;

            case GripperState::Fault:
                duty_cycle = 0.0F;
                return std::unexpected(error_);
        }

        return duty_cycle;
    }

    [[nodiscard]] GripperTelemetry telemetry() const noexcept {
        return GripperTelemetry{
            .state = state_,
            .error = error_,
            .current_force_n = last_current_a_ * cfg_.current_to_force_ratio,
            .motor_current_a = last_current_a_,
            .jaw_position_mm = last_pos_mm_
        };
    }

private:
    Config cfg_;
    GripperState state_{GripperState::Idle};
    GripperError error_{GripperError::None};
    float target_force_n_{0.0F};
    float integral_accum_{0.0F};
    float last_current_a_{0.0F};
    float last_pos_mm_{0.0F};
    uint32_t state_elapsed_ms_{0};
};

} // namespace drone::manipulator
