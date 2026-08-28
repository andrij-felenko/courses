// ============================================================================
// digital_avr.hpp — Об'єктно-орієнтований цифровий регулятор напруги (C++20)
// ============================================================================
#pragma once

#include <algorithm>
#include <concepts>
#include <expected>
#include <numbers>
#include <span>

namespace electronics::power {

enum class AvrStatus : uint8_t {
    NormalOperation,
    LoadDumpTripped,
    SensorFault,
    ThermalWarning
};

struct AvrConfig {
    float target_voltage_base{14.4f};
    float temp_coefficient{-0.015f};
    float kp{0.35f};
    float ki{1.80f};
    float kd{0.008f};
    float duty_min{0.0f};
    float duty_max{1.0f};
    float lrc_slew_rate{0.25f};
    float load_dump_threshold{16.5f};
    float load_dump_slope{50.0f};     // Градієнт В/мс
};

class DigitalAvr {
public:
    explicit constexpr DigitalAvr(const AvrConfig& config = {}) noexcept
        : cfg_{config}, v_filtered_{config.target_voltage_base}, prev_v_raw_{config.target_voltage_base} {}

    [[nodiscard]] std::expected<float, AvrStatus> update(float v_raw, float temp_c, float dt_seconds) noexcept {
        if (dt_seconds <= 0.0f || std::isnan(v_raw) || std::isnan(temp_c)) {
            return std::unexpected(AvrStatus::SensorFault);
        }

        // 1. Цифрова фільтрація напруги від пульсацій моста Ларіонова
        constexpr float kAlpha = 0.125f;
        v_filtered_ += kAlpha * (v_raw - v_filtered_);

        // 2. Детектування швидкого скидання навантаження (Load Dump)
        const float dv_dt = (v_raw - prev_v_raw_) / (dt_seconds * 1000.0f);
        prev_v_raw_ = v_raw;

        if (v_raw >= cfg_.load_dump_threshold || dv_dt >= cfg_.load_dump_slope) {
            load_dump_active_ = true;
            current_duty_ = 0.0f;
            integral_sum_ = 0.0f;
            return std::unexpected(AvrStatus::LoadDumpTripped);
        }

        if (load_dump_active_) {
            if (v_raw <= cfg_.target_voltage_base) {
                load_dump_active_ = false;
            } else {
                return std::unexpected(AvrStatus::LoadDumpTripped);
            }
        }

        // 3. Адаптивна температурна корекція робочої точки
        float v_target = cfg_.target_voltage_base + cfg_.temp_coefficient * (temp_c - 25.0f);
        v_target = std::clamp(v_target, 13.2f, 15.2f);

        // 4. Розрахунок ланок ПІД-регулятора
        const float error = v_target - v_filtered_;
        const float p_term = cfg_.kp * error;
        const float d_term = cfg_.kd * (error - prev_error_) / dt_seconds;
        prev_error_ = error;

        // Anti-Windup: накопичення інтегратора лише всередині лінійного діапазону
        const float tentative_duty = p_term + integral_sum_ + (cfg_.ki * error * dt_seconds) + d_term;
        if (tentative_duty >= cfg_.duty_min && tentative_duty <= cfg_.duty_max) {
            integral_sum_ += cfg_.ki * error * dt_seconds;
        }

        const float calculated_duty = std::clamp(p_term + integral_sum_ + d_term, cfg_.duty_min, cfg_.duty_max);

        // 5. Обмеження швидкості зміни струму збудження (LRC)
        const float max_step = cfg_.lrc_slew_rate * dt_seconds;
        if (calculated_duty > current_duty_ + max_step) {
            current_duty_ += max_step;
        } else {
            current_duty_ = calculated_duty;
        }

        return current_duty_;
    }

    [[nodiscard]] constexpr float filtered_voltage() const noexcept { return v_filtered_; }
    [[nodiscard]] constexpr float duty_cycle() const noexcept { return current_duty_; }
    [[nodiscard]] constexpr bool is_load_dump_active() const noexcept { return load_dump_active_; }

    constexpr void reset_faults() noexcept {
        load_dump_active_ = false;
        integral_sum_ = 0.0f;
    }

private:
    AvrConfig cfg_;
    float v_filtered_{14.4f};
    float prev_v_raw_{14.4f};
    float prev_error_{0.0f};
    float integral_sum_{0.0f};
    float current_duty_{0.0f};
    bool load_dump_active_{false};
};

} // namespace electronics::power
