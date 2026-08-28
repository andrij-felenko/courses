// ThermalMonitor.hpp — Ідіоматичний C++20 клас моніторингу
#pragma once
#include <algorithm>
#include <cmath>

namespace drone::propulsion {

struct ThermalLimits {
    float r_phase_20c{0.050f};         // Опір фази мотора при 20°C (Ом)
    float alpha_cu{0.00393f};          // Температурний коефіцієнт міді
    float c_th_winding{4.2f};          // Теплоємність обмотки (Дж/°C)
    float r_th_wind_to_air{2.5f};      // Тепловий опір обмотка-повітря (°C/Вт)
    float esc_temp_limit_c{105.0f};    // Гранична температура ESC (°C)
    float motor_temp_limit_c{125.0f};  // Гранична температура обмотки (°C)
};

class ThermalMonitor {
public:
    explicit constexpr ThermalMonitor(const ThermalLimits& limits, float ambient_c = 25.0f) noexcept
        : limits_{limits}, motor_temp_est_{ambient_c}, esc_temp_c_{ambient_c} {}

    void update(float phase_current_rms, float esc_telemetry_temp,
                float ambient_temp_c, float dt_sec) noexcept {
        if (dt_sec <= 0.0f) return;
        esc_temp_c_ = esc_telemetry_temp;

        // 1. Оцінка температури обмотки
        const float r_cu = limits_.r_phase_20c * (1.0f + limits_.alpha_cu * (motor_temp_est_ - 20.0f));
        const float p_loss_cu = 1.5f * phase_current_rms * phase_current_rms * r_cu;
        const float heat_dissipated = (motor_temp_est_ - ambient_temp_c) / limits_.r_th_wind_to_air;

        const float d_temp = (p_loss_cu - heat_dissipated) / limits_.c_th_winding;
        motor_temp_est_ += d_temp * dt_sec;

        // 2. Термотротлінг
        auto calc_scale = [](float val, float limit, float window) noexcept -> float {
            const float warn = limit - window;
            if (val <= warn) return 1.0f;
            if (val >= limit) return 0.3f;
            return std::clamp(1.0f - (val - warn) / window, 0.3f, 1.0f);
        };

        const float scale_esc = calc_scale(esc_temp_c_, limits_.esc_temp_limit_c, 20.0f);
        const float scale_mot = calc_scale(motor_temp_est_, limits_.motor_temp_limit_c, 25.0f);

        max_allowed_throttle_ = std::min(scale_esc, scale_mot);
        thermal_alert_ = (max_allowed_throttle_ < 0.95f);
    }

    [[nodiscard]] constexpr float motor_temperature() const noexcept { return motor_temp_est_; }
    [[nodiscard]] constexpr float esc_temperature() const noexcept { return esc_temp_c_; }
    [[nodiscard]] constexpr float throttle_limit() const noexcept { return max_allowed_throttle_; }
    [[nodiscard]] constexpr bool is_alert() const noexcept { return thermal_alert_; }

private:
    ThermalLimits limits_;
    float motor_temp_est_{25.0f};
    float esc_temp_c_{25.0f};
    float max_allowed_throttle_{1.0f};
    bool  thermal_alert_{false};
};

} // namespace drone::propulsion
