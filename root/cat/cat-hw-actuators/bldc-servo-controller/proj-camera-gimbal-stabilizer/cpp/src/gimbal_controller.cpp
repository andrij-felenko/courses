#include "gimbal_controller.hpp"

namespace gimbal {

bool GimbalController::init(const GimbalConfig& config) {
    config_ = config;

    // 1. Ініціалізація датчика IMU через шину SPI
    if (!imu_handler_.init(config_.imu_cfg)) {
        return false;
    }

    // 2. Налаштування каскадного ПІД-регулятора та режекторного фільтра
    cascade_pid_.set_angle_gains(config_.angle_pid);
    cascade_pid_.set_velocity_gains(config_.velocity_pid);
    cascade_pid_.configure_notch_filter(
        config_.notch_center_freq_hz,
        config_.notch_bandwidth_hz,
        config_.loop_frequency_hz
    );

    // 3. Ініціалізація векторного модулятора FOC
    foc_modulator_.init(config_.motor_pole_pairs, config_.bus_voltage_v);

    enabled_ = true;
    telemetry_.is_active = true;
    return true;
}

void GimbalController::set_target_angle(float angle_rad) {
    target_angle_rad_ = angle_rad;
}

void GimbalController::set_enabled(bool enable) {
    enabled_ = enable;
    if (!enabled_) {
        cascade_pid_.reset();
    }
    telemetry_.is_active = enabled_;
}

void GimbalController::process_loop() {
    if (!enabled_) {
        return;
    }

    // 1. Синхронне опитування інерціального IMU-датчика по SPI
    ImuData imu_data{};
    if (!imu_handler_.read_sensor(imu_data)) {
        return;
    }

    float dt = 1.0f / config_.loop_frequency_hz;

    // 2. Обчислення каскадного ПІД-регулятора з внутрішньою Notch-фільтрацією
    float iq_cmd = cascade_pid_.update(
        target_angle_rad_,
        imu_data.angle_rad,
        imu_data.gyro_rad_s,
        dt
    );

    // 3. Формування вектора напруги FOC (Direct Id = 0 для максимального моменту)
    DQ target_dq;
    target_dq.d = 0.0f;
    target_dq.q = iq_cmd;

    // 4. Перетворення Кларка/Парка та генерування просторово-векторного ШІМ (SVPWM)
    DutyCycles pwm_duties = foc_modulator_.update(target_dq, imu_data.angle_rad);

    // 5. Оновлення телеметрії та видача на силові ключі трифазного інвертора
    telemetry_.imu_data = imu_data;
    telemetry_.target_angle_rad = target_angle_rad_;
    telemetry_.iq_command = iq_cmd;
    telemetry_.pwm_duties = pwm_duties;
}

} // namespace gimbal
