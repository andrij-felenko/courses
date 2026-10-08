#include <iostream>
#include <iomanip>
#include <chrono>
#include <thread>
#include "gimbal_controller.hpp"

using namespace gimbal;

int main() {
    std::cout << "=== Ініціалізація сервоконтролера підвісу BLDC (C++ FOC) ===" << std::endl;

    // Створення конфігурації підсистеми стабілізації
    GimbalConfig config;

    // Конфігурація SPI IMU
    config.imu_cfg.cs_pin = 10;
    config.imu_cfg.spi_speed_hz = 8000000;
    config.imu_cfg.gyro_lsb_per_dps = 16.4f;
    config.imu_cfg.accel_lsb_per_g = 2048.0f;

    // Конфігурація каскадного ПІД
    config.angle_pid = { /*kp=*/ 6.5f, /*ki=*/ 0.1f, /*kd=*/ 0.0f, /*max_out=*/ 15.0f, /*limit=*/ 2.0f };
    config.velocity_pid = { /*kp=*/ 1.2f, /*ki=*/ 0.05f, /*kd=*/ 0.01f, /*max_out=*/ 10.0f, /*limit=*/ 5.0f };

    // Налаштування цифрового режекторного фільтра (пригнічення вібрації 50 Гц)
    config.notch_center_freq_hz = 50.0f;
    config.notch_bandwidth_hz = 10.0f;

    // Параметри BLDC мотора та FOC
    config.motor_pole_pairs = 7;
    config.bus_voltage_v = 12.0f;
    config.loop_frequency_hz = 1000.0f; // 1 кГц дискретизація

    GimbalController controller;
    if (!controller.init(config)) {
        std::cerr << "Помилка: не вдалося ініціалізувати GimbalController!" << std::endl;
        return -1;
    }

    std::cout << "Система успішно ініціалізована. Запуск контуру стабілізації..." << std::endl;

    // Задання цільового кута у 0.15 радіан (~8.6 градусів)
    float target_angle = 0.15f;
    controller.set_target_angle(target_angle);

    // Імітація високочастотного таймерного переривання (1000 Гц)
    for (int step = 0; step < 10; ++step) {
        controller.process_loop();

        const auto& telemetry = controller.get_telemetry();

        std::cout << std::fixed << std::setprecision(4)
                  << "[Крок " << std::setw(2) << step << "] "
                  << "Ціль: " << telemetry.target_angle_rad << " рад | "
                  << "Кут IMU: " << telemetry.imu_data.angle_rad << " рад | "
                  << "Iq cmd: " << telemetry.iq_command << " V | "
                  << "ШІМ [A,B,C]: [" 
                  << telemetry.pwm_duties.a << ", "
                  << telemetry.pwm_duties.b << ", "
                  << telemetry.pwm_duties.c << "]" 
                  << std::endl;
    }

    std::cout << "Завершення роботи контролера." << std::endl;
    return 0;
}
