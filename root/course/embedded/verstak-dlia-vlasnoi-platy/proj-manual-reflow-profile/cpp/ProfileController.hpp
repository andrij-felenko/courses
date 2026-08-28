// ProfileController.hpp - Керування термопрофілем (C++20)
#pragma once

#include <array>
#include <cstdint>
#include <span>
#include <algorithm>
#include <cmath>
#include <expected>

namespace embedded::thermal {

enum class Stage : uint8_t {
    Idle = 0,
    Preheat,
    Soak,
    Reflow,
    Cooldown,
    ErrorFault
};

enum class Fault : uint8_t {
    None = 0,
    SensorDisconnected,
    ThermalRunaway,
    OverheatLimit
};

struct StageConfig {
    float target_temp_c;
    float ramp_rate_c_per_s;
    uint32_t hold_time_s;
};

class PidController {
public:
    constexpr PidController(float kp, float ki, float kd, float int_limit, float d_filter = 0.7f) noexcept
        : kp_(kp), ki_(ki), kd_(kd), integral_limit_(int_limit), d_filter_(d_filter) {}

    void reset() noexcept {
        integral_ = 0.0f;
        prev_error_ = 0.0f;
        filtered_derivative_ = 0.0f;
    }

    [[nodiscard]] float calculate(float setpoint, float measured, float dt_s) noexcept {
        const float error = setpoint - measured;
        
        // Інтегрування з анти-віндапом (обмеження накопичення)
        integral_ += error * dt_s;
        integral_ = std::clamp(integral_, -integral_limit_, integral_limit_);

        // Диференціювання з фільтром низьких частот першого порядку
        const float raw_derivative = (dt_s > 0.0f) ? ((error - prev_error_) / dt_s) : 0.0f;
        filtered_derivative_ = (d_filter_ * filtered_derivative_) + ((1.0f - d_filter_) * raw_derivative);
        prev_error_ = error;

        const float output = (kp_ * error) + (ki_ * integral_) + (kd_ * filtered_derivative_);
        return std::clamp(output, 0.0f, 1.0f);
    }

private:
    float kp_;
    float ki_;
    float kd_;
    float integral_limit_;
    float d_filter_;
    float integral_{0.0f};
    float prev_error_{0.0f};
    float filtered_derivative_{0.0f};
};

class ReflowController {
public:
    static constexpr size_t kStageCount = 4;
    static constexpr float kMaxSafeTempC = 270.0f;
    static constexpr float kMinRunawayRiseC = 2.0f; // Мінімально очікуваний підйом T за 15 с при 100% потужності

    explicit ReflowController(std::array<StageConfig, kStageCount> config) noexcept
        : stages_(config), pid_(0.035f, 0.0008f, 0.18f, 40.0f, 0.75f) {}

    void start() noexcept {
        if (stage_ == Stage::Idle) {
            stage_ = Stage::Preheat;
            current_stage_idx_ = 0;
            stage_timer_s_ = 0;
            runaway_counter_s_ = 0;
            target_temp_ = 25.0f;
            pid_.reset();
            fault_ = Fault::None;
        }
    }

    void abort(Fault reason) noexcept {
        stage_ = Stage::ErrorFault;
        fault_ = reason;
        duty_cycle_ = 0.0f;
    }

    [[nodiscard]] Stage current_stage() const noexcept { return stage_; }
    [[nodiscard]] Fault current_fault() const noexcept { return fault_; }
    [[nodiscard]] float duty_cycle() const noexcept { return duty_cycle_; }
    [[nodiscard]] float target_temp() const noexcept { return target_temp_; }

    void tick_1s(std::expected<float, Fault> sensor_reading) noexcept {
        if (!sensor_reading.has_value()) {
            abort(sensor_reading.error());
            return;
        }

        const float current_temp = sensor_reading.value();
        if (current_temp > kMaxSafeTempC) {
            abort(Fault::OverheatLimit);
            return;
        }

        if (stage_ == Stage::Idle || stage_ == Stage::ErrorFault) {
            duty_cycle_ = 0.0f;
            return;
        }

        // Перевірка захисту від теплового розгону (Thermal Runaway Watchdog)
        if (duty_cycle_ > 0.95f) {
            if (current_temp - temp_at_full_power_ < kMinRunawayRiseC) {
                runaway_counter_s_++;
                if (runaway_counter_s_ >= 15) {
                    abort(Fault::ThermalRunaway);
                    return;
                }
            } else {
                runaway_counter_s_ = 0;
                temp_at_full_power_ = current_temp;
            }
        } else {
            runaway_counter_s_ = 0;
            temp_at_full_power_ = current_temp;
        }

        process_stage_progression(current_temp);
        duty_cycle_ = pid_.calculate(target_temp_, current_temp, 1.0f);
    }

private:
    void process_stage_progression(float current_temp) noexcept {
        const auto& cfg = stages_[current_stage_idx_];

        // Плавне зміщення уставки за заданим рампом
        if (target_temp_ < cfg.target_temp_c) {
            target_temp_ += cfg.ramp_rate_c_per_s;
            if (target_temp_ > cfg.target_temp_c) target_temp_ = cfg.target_temp_c;
        } else if (target_temp_ > cfg.target_temp_c) {
            target_temp_ -= cfg.ramp_rate_c_per_s;
            if (target_temp_ < cfg.target_temp_c) target_temp_ = cfg.target_temp_c;
        }

        // Перевірка стабілізації та відліку часу витримки
        if (std::abs(current_temp - cfg.target_temp_c) <= 3.0f || target_temp_ == cfg.target_temp_c) {
            stage_timer_s_++;
            if (stage_timer_s_ >= cfg.hold_time_s) {
                advance_stage();
            }
        }
    }

    void advance_stage() noexcept {
        stage_timer_s_ = 0;
        current_stage_idx_++;
        if (current_stage_idx_ >= kStageCount) {
            stage_ = Stage::Idle;
            duty_cycle_ = 0.0f;
            target_temp_ = 25.0f;
        } else {
            stage_ = static_cast<Stage>(current_stage_idx_ + 1);
        }
    }

    std::array<StageConfig, kStageCount> stages_;
    PidController pid_;
    Stage stage_{Stage::Idle};
    Fault fault_{Fault::None};
    size_t current_stage_idx_{0};
    uint32_t stage_timer_s_{0};
    uint32_t runaway_counter_s_{0};
    float target_temp_{25.0f};
    float duty_cycle_{0.0f};
    float temp_at_full_power_{25.0f};
};

} // namespace embedded::thermal
