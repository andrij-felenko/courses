#include "servo_pwm.hpp"
#include "current_monitor.hpp"
#include "servo_calibrator.hpp"
#include "display_telemetry.hpp"
#include <iostream>
#include <vector>

int main() {
    using namespace actuators;

    std::cout << "=== Запуск прошивки сервокалібратора MG90S V2 ===" << std::endl;

    // 1. Конфігурація генератора ШІМ та монітора струму
    ServoPwmConfig pwm_config;
    pwm_config.pin = 9;
    pwm_config.min_pulse_us = 500;
    pwm_config.max_pulse_us = 2500;
    pwm_config.min_angle_deg = 0.0f;
    pwm_config.max_angle_deg = 180.0f;

    CurrentMonitorConfig mon_config;
    mon_config.stall_threshold_ma = 650.0f; // Поріг струму заклинювання редуктора MG90S
    mon_config.stall_confirm_samples = 3;

    // 2. Створення екземплярів модулів
    ServoPwmGenerator pwm_gen(pwm_config);
    CurrentMonitor current_mon(mon_config);
    ServoCalibrator calibrator(pwm_gen, current_mon);
    DisplayTelemetry telemetry;

    // 3. Ініціалізація системи
    calibrator.initialize();
    
    // Встановлюємо робочі межі калібрування для конкретного механізму (10.0° - 170.0°)
    CalibrationLimits custom_limits;
    custom_limits.min_angle_deg = 10.0f;
    custom_limits.max_angle_deg = 170.0f;
    calibrator.set_limits(custom_limits);

    // -------------------------------------------------------------
    // ЕТАП 1: Ручний режим позиціонування
    // -------------------------------------------------------------
    std::cout << "\n--- ЕТАП 1: Ручне налаштування позиції ---" << std::endl;
    calibrator.set_mode(CalibratorMode::Manual);

    std::vector<float> manual_angles = {10.0f, 45.0f, 90.0f, 135.0f, 170.0f};
    for (float angle : manual_angles) {
        calibrator.set_target_angle(angle);
        // Симулюємо нормальне споживання струму при русі (110 - 150 мА)
        calibrator.update_simulated(120.0f + (angle * 0.15f));
        
        TelemetryFrame frame = telemetry.capture_frame(calibrator, pwm_gen, current_mon);
        telemetry.render_log_line(frame);
    }

    // -------------------------------------------------------------
    // ЕТАП 2: Калібрування крайніх точок
    // -------------------------------------------------------------
    std::cout << "\n--- ЕТАП 2: Фіксація нових крайніх точок ---" << std::endl;
    calibrator.set_target_angle(15.0f);
    calibrator.update_simulated(130.0f);
    if (calibrator.calibrate_current_as_min()) {
        std::cout << "Успішно відкалібровано НИЖНЮ межу: " << pwm_gen.get_current_angle() << " deg" << std::endl;
    }

    calibrator.set_target_angle(165.0f);
    calibrator.update_simulated(135.0f);
    if (calibrator.calibrate_current_as_max()) {
        std::cout << "Успішно відкалібровано ВЕРХНЮ межу: " << pwm_gen.get_current_angle() << " deg" << std::endl;
    }

    // -------------------------------------------------------------
    // ЕТАП 3: Автоматичне покрокове сканування
    // -------------------------------------------------------------
    std::cout << "\n--- ЕТАП 3: Автоматичне сканування діапазону ---" << std::endl;
    calibrator.set_scan_params(15.0f, true);
    calibrator.set_mode(CalibratorMode::AutoScan);

    for (int tick = 0; tick < 8; ++tick) {
        calibrator.update_simulated(140.0f);
        TelemetryFrame frame = telemetry.capture_frame(calibrator, pwm_gen, current_mon);
        telemetry.render_log_line(frame);
    }

    // -------------------------------------------------------------
    // ЕТАП 4: Симуляція заклинювання редуктора та спрацювання захисту
    // -------------------------------------------------------------
    std::cout << "\n--- ЕТАП 4: Виявлення заклинювання редуктора (Stall Current) ---" << std::endl;
    std::cout << "[ПОДІЯ] Фізичне блокування ротора! Струм зростає до 780 мА..." << std::endl;

    // Подаємо перевищення струму в декількох такт-циклах для спрацювання струмового захисту
    for (int i = 0; i < 4; ++i) {
        calibrator.update_simulated(780.0f); // 780 мА > threshold (650 мА)
    }

    TelemetryFrame emergency_frame = telemetry.capture_frame(calibrator, pwm_gen, current_mon);
    telemetry.render_screen(emergency_frame);

    // -------------------------------------------------------------
    // ЕТАП 5: Усунення заклинювання та повернення в робочий стан
    // -------------------------------------------------------------
    std::cout << "\n--- ЕТАП 5: Скидання аварії та відновлення керування ---" << std::endl;
    std::cout << "[ДІЯ] Видалення перешкоди, виклик reset_emergency_stop()..." << std::endl;
    calibrator.reset_emergency_stop();
    calibrator.set_target_angle(90.0f);
    calibrator.update_simulated(115.0f);

    TelemetryFrame final_frame = telemetry.capture_frame(calibrator, pwm_gen, current_mon);
    telemetry.render_screen(final_frame);

    std::cout << "=== Завершення роботи програми ===" << std::endl;
    return 0;
}
