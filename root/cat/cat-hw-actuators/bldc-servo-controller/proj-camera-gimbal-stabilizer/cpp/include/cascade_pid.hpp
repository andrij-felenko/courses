#pragma once

#include "notch_filter.hpp"

namespace gimbal {

/// @brief Параметри ПІД-регулятора
struct PidGains {
    float kp{0.0f};               ///< Пропорційний коефіцієнт
    float ki{0.0f};               ///< Інтегральний коефіцієнт
    float kd{0.0f};               ///< Диференціальний коефіцієнт
    float max_output{0.0f};       ///< Максимальне обмеження виходу
    float integrator_limit{0.0f}; ///< Обмеження насичення інтегратора (Anti-windup)
};

/// @brief Двоконтурний каскадний ПІД-контролер стабілізації (Кут -> Швидкість -> Струм q)
class CascadePidController {
public:
    CascadePidController() = default;

    /// @brief Встановлення коефіцієнтів зовнішнього контуру позиціонування за кутом
    void set_angle_gains(const PidGains& gains) { angle_gains_ = gains; }

    /// @brief Встановлення коефіцієнтів внутрішнього контуру регулювання швидкості
    void set_velocity_gains(const PidGains& gains) { velocity_gains_ = gains; }

    /// @brief Ініціалізація внутрішнього Notch-фільтра контуру швидкості
    void configure_notch_filter(float center_freq_hz, float bw_hz, float sample_rate_hz);

    /// @brief Розрахунок та оновлення каскадного контуру стабілізації
    /// @param target_angle_rad Заданий цільовий кут (рад)
    /// @param measured_angle_rad Виміряний кут від IMU (рад)
    /// @param measured_velocity_rad_s Виміряна кутова швидкість від IMU (рад/с)
    /// @param dt Крок часу дискретизації (с)
    /// @return Обчислене задання квадратурного струму Iq (А або В)
    float update(float target_angle_rad, float measured_angle_rad, float measured_velocity_rad_s, float dt);

    /// @brief Скидання стану інтеграторів та затримок
    void reset();

    /// @brief Телеметричні методи зчитування проміжних сигналів
    float get_target_velocity() const { return target_velocity_; }
    float get_filtered_velocity() const { return filtered_velocity_; }
    float get_iq_cmd() const { return iq_cmd_; }

private:
    /// @brief Допоміжне обмеження величини змінної
    static float clamp(float value, float min_val, float max_val);

    PidGains angle_gains_{};
    PidGains velocity_gains_{};

    NotchFilter notch_filter_{};

    float angle_integral_{0.0f};
    float velocity_integral_{0.0f};
    float last_velocity_error_{0.0f};

    float target_velocity_{0.0f};
    float filtered_velocity_{0.0f};
    float iq_cmd_{0.0f};
};

} // namespace gimbal
