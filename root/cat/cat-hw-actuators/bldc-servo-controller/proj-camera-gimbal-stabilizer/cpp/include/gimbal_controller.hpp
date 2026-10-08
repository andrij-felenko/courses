#pragma once

#include "imu_spi.hpp"
#include "cascade_pid.hpp"
#include "foc_modulator.hpp"

namespace gimbal {

/// @brief Конфігурація всього сервоконтролера стабілізації підвісу
struct GimbalConfig {
    ImuConfig imu_cfg{};
    PidGains angle_pid{};
    PidGains velocity_pid{};
    float notch_center_freq_hz{50.0f};
    float notch_bandwidth_hz{15.0f};
    uint8_t motor_pole_pairs{7};
    float bus_voltage_v{12.0f};
    float loop_frequency_hz{1000.0f};
};

/// @brief Повний стан телеметрії контролера підвісу
struct GimbalTelemetry {
    ImuData imu_data{};
    float target_angle_rad{0.0f};
    float iq_command{0.0f};
    DutyCycles pwm_duties{};
    bool is_active{false};
};

/// @brief Головний C++ клас контролера підвісу
class GimbalController {
public:
    GimbalController() = default;
    ~GimbalController() = default;

    /// @brief Ініціалізація периферифії, підсистем IMU, ПІД та FOC
    bool init(const GimbalConfig& config);

    /// @brief Задання цільового кута стабілізації підвісу
    void set_target_angle(float angle_rad);

    /// @brief Основний високочастотний контур регулювання (викликається у таймерному перериванні)
    void process_loop();

    /// @brief Увімкнення / вимкнення контуру стабілізації
    void set_enabled(bool enable);

    /// @brief Отримання поточного стану телеметрії
    const GimbalTelemetry& get_telemetry() const { return telemetry_; }

private:
    GimbalConfig config_{};
    SpiImuHandler imu_handler_{};
    CascadePidController cascade_pid_{};
    FocModulator foc_modulator_{};

    GimbalTelemetry telemetry_{};
    float target_angle_rad_{0.0f};
    bool enabled_{false};
};

} // namespace gimbal
