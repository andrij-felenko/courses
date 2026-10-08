#ifndef SERVO_CALIBRATOR_HPP
#define SERVO_CALIBRATOR_HPP

#include "servo_pwm.hpp"
#include "current_monitor.hpp"
#include <string_view>

namespace actuators {

/// @brief Режими роботи конечного автомата сервокалібратора.
enum class CalibratorMode {
    Disabled,        // Вимкнений стан (ШІМ деактивовано)
    Manual,          // Ручне керування позиціонуванням
    AutoScan,        // Автоматичне сканування між крайніми точками
    EmergencyStop    // Аварійна зупинка при заклинюванні редуктора
};

/// @brief Структура збереження межевих калібрувальних параметрів.
struct CalibrationLimits {
    float min_angle_deg{5.0f};          // Калібрована нижня межа кута
    float max_angle_deg{175.0f};        // Калібрована верхня межа кута
    uint16_t min_pulse_us{550};         // Відповідна тривалість мінімального імпульсу
    uint16_t max_pulse_us{2450};        // Відповідна тривалість максимального імпульсу
};

/// @brief Головний клас-координатор сервокалібратора MG90S V2.
class ServoCalibrator {
public:
    ServoCalibrator(ServoPwmGenerator& pwm_gen, CurrentMonitor& current_mon);

    /// @brief Початкова ініціалізація калібратора.
    bool initialize();

    /// @brief Крок виконання основного циклу обробки з сирим АЦП вибірки струму.
    /// @param raw_adc_current Сирий відлік АЦП струму.
    void update(uint16_t raw_adc_current);

    /// @brief Крок виконання з прямим значенням струму (для випробувань).
    /// @param current_ma Струм споживання в мА.
    void update_simulated(float current_ma);

    /// @brief Перемикання режиму роботи конечного автомата.
    bool set_mode(CalibratorMode mode);

    /// @brief Отримання поточного режиму роботи.
    CalibratorMode get_mode() const;

    /// @brief Текстова назва поточного режиму для телеметрії.
    std::string_view get_mode_name() const;

    /// @brief Встановлення Цільового кута (працює у режимі Manual).
    bool set_target_angle(float angle_deg);

    /// @brief Зміщення кута на заданий крок (+/- deg).
    bool step_angle(float delta_deg);

    /// @brief Налаштування параметрів автоматичного сканування.
    void set_scan_params(float step_deg, bool auto_reverse);

    /// @brief Задання меж калібрування.
    void set_limits(const CalibrationLimits& limits);

    /// @brief Отримання поточних меж калібрування.
    const CalibrationLimits& get_limits() const;

    /// @brief Фіксація поточної позиції як мінімальної калібрувальної межі.
    bool calibrate_current_as_min();

    /// @brief Фіксація поточної позиції як максимальної калібрувальної межі.
    bool calibrate_current_as_max();

    /// @brief Перевірка наявності стану аварійної зупинки.
    bool is_emergency_stop() const;

    /// @brief Скидання аварійного стану та відновлення роботи.
    void reset_emergency_stop();

private:
    ServoPwmGenerator& pwm_;
    CurrentMonitor& monitor_;
    CalibratorMode mode_{CalibratorMode::Disabled};
    CalibrationLimits limits_{};

    float target_angle_deg_{90.0f};
    float scan_step_deg_{1.0f};
    bool scan_direction_forward_{true};
    bool auto_reverse_scan_{true};

    void process_auto_scan();
    void enforce_safety_check();
};

} // namespace actuators

#endif // SERVO_CALIBRATOR_HPP
