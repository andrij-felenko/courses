#pragma once

#include <cstdint>
#include <cstddef>
#include <span>

namespace actuator {

/// @brief Робочий стан шарнірного привода
enum class ActuatorState : uint8_t {
    Disabled,          ///< Привод знеструмлений (генерацію ШІМ вимкнено, утримувальний момент знято)
    Idle,              ///< Вал перебуває в цільовій позиції, навантаження в нормі
    Moving,            ///< Відбувається плавне траєкторне переміщення вала з контролем швидкості
    Compliant,         ///< Режим адаптивного поступлення під дією зовнішнього механічного опору
    EmergencyStopped   ///< Аварійно знеструмлений через небезпечне механічне перевантаження або заклинювання
};

/// @brief Діагностичний статус навантаження за споживанням струму
enum class FaultState : uint8_t {
    Normal,            ///< Струм споживання в допустимих межах холостого або штатного руху
    Warning,           ///< Струм перевищує номінальний рівень тривалого руху
    StallDetected      ///< Зафіксовано блокування вала (надструм перевищив аварійний поріг і таймаут)
};

/// @brief Параметри геометрії, ШІМ та обмеження швидкості вала (SG90, SG92R, MG90S, MG90D)
struct ActuatorConfig {
    float min_angle_deg{0.0f};           ///< Мінімальний фізичний кут шарніра (зазвичай 0.0°)
    float max_angle_deg{180.0f};         ///< Максимальний фізичний кут шарніра (зазвичай 180.0°)
    uint16_t min_pulse_us{500};          ///< Тривалість імпульсу ШІМ для min_angle_deg (500–600 мкс)
    uint16_t max_pulse_us{2500};         ///< Тривалість імпульсу ШІМ для max_angle_deg (2400–2500 мкс)
    float max_velocity_deg_s{120.0f};    ///< Ліміт кутової швидкості (°/с) для запобігання сколюванню шестерень
    float compliance_step_deg{5.0f};     ///< Крок відступу вала при спрацьовуванні адаптивної податливості
};

/// @brief Параметри струмового захисту та цифрової фільтрації
struct CurrentMonitorConfig {
    uint32_t warning_current_ma{400};    ///< Поріг підвищеного навантаження (мА)
    uint32_t stall_current_ma{650};      ///< Поріг струму блокування вала (мА) для розпізнавання stall-режиму
    uint32_t stall_timeout_ms{250};      ///< Час утримання надструму для підтвердження блокування вала (мс)
    uint32_t blanking_time_ms{80};       ///< Інтервал відсікання пускового сплеску розгону ротора (inrush blanking, мс)
    float filter_alpha{0.25f};           ///< Ваговий коефіцієнт експоненційного згладжування вибірок (0.0 < alpha <= 1.0)
};

/// @brief Покажчик на функцію запису тривалості імпульсу ШІМ в апаратний таймер мікроконтролера
using PwmWriteCallback = void (*)(uint16_t pulse_us, void* user_data);

/// @brief Покажчик на функцію зворотного виклику при детекції аварійного струму заклинювання
using StallFaultCallback = void (*)(FaultState fault, uint32_t filtered_current_ma, void* user_data);

/// @brief Клас привода шарніра: керування кутом, профілювання швидкості та захисне розвантаження
class JointActuator {
public:
    explicit JointActuator(const ActuatorConfig& config);
    ~JointActuator();

    JointActuator(const JointActuator&) = delete;
    JointActuator& operator=(const JointActuator&) = delete;
    JointActuator(JointActuator&&) noexcept = default;
    JointActuator& operator=(JointActuator&&) noexcept = default;

    /// @brief Реєстрація апаратного адаптера генерації ШІМ
    void setPwmSink(PwmWriteCallback callback, void* user_data = nullptr) noexcept;

    /// @brief Ініціалізація вала в початкове безпечне положення
    bool init(float initial_angle_deg, uint32_t current_time_ms);

    /// @brief Встановлення нового цільового кута шарніра
    bool setTargetAngle(float angle_deg);

    /// @brief Адаптивне кутове поступлення (податливість) під дією зовнішнього механічного опору
    /// @param retreat_direction Напрямок відступу (-1.0f: у бік зменшення кута, +1.0f: у бік збільшення)
    void applyCompliance(float retreat_direction);

    /// @brief Аварійне зняття сигналу керування (деактивація ШІМ для вимкнення моменту утримання)
    void emergencyStop();

    /// @brief Увімкнення генерації керувального сигналу ШІМ
    void enable();

    /// @brief Планове знеструмлення привода
    void disable();

    /// @brief Скидання аварійного стану після усунення перешкоди
    void resetFault(uint32_t current_time_ms);

    /// @brief Періодичний неблокувальний крок траєкторного оновлення положення вала
    void update(uint32_t current_time_ms);

    [[nodiscard]] float getCurrentAngle() const noexcept { return current_angle_deg_; }
    [[nodiscard]] float getTargetAngle() const noexcept { return target_angle_deg_; }
    [[nodiscard]] ActuatorState getState() const noexcept { return state_; }
    [[nodiscard]] bool isEnabled() const noexcept { return is_enabled_; }

private:
    [[nodiscard]] uint16_t calculatePulseWidthUs(float angle_deg) const noexcept;
    void sendPulse(uint16_t pulse_us) noexcept;

    ActuatorConfig config_;
    PwmWriteCallback pwm_sink_{nullptr};
    void* pwm_user_data_{nullptr};
    float current_angle_deg_{0.0f};
    float target_angle_deg_{0.0f};
    uint32_t last_update_ms_{0};
    ActuatorState state_{ActuatorState::Disabled};
    bool is_enabled_{false};
};

/// @brief Клас контролю струму: фільтрація, калібрування зсуву та виявлення заклинювання редуктора
class JointCurrentMonitor {
public:
    explicit JointCurrentMonitor(const CurrentMonitorConfig& config);
    ~JointCurrentMonitor() = default;

    JointCurrentMonitor(const JointCurrentMonitor&) = delete;
    JointCurrentMonitor& operator=(const JointCurrentMonitor&) = delete;
    JointCurrentMonitor(JointCurrentMonitor&&) noexcept = default;
    JointCurrentMonitor& operator=(JointCurrentMonitor&&) noexcept = default;

    /// @brief Реєстрація функції зворотного виклику для сповіщення про аварійні події
    void setStallCallback(StallFaultCallback callback, void* user_data = nullptr) noexcept;

    /// @brief Програмне калібрування початкового апаратного зсуву струмового датчика у стані спокою
    /// @param zero_samples Буфер вибірок АЦП у стані спокою
    bool calibrateZeroOffset(std::span<const uint32_t> zero_samples);

    /// @brief Сповіщення про початок руху для запуску вікна відсікання пускового сплеску струму
    void notifyMotionStarted(uint32_t current_time_ms) noexcept;

    /// @brief Періодична цифрова фільтрація вибірки АЦП та детекція тривалого струму блокування
    /// @param raw_current_ma Миттєве виміряне значення струму з сенсора (мА)
    /// @param current_time_ms Поточний системний час (мс)
    void update(uint32_t raw_current_ma, uint32_t current_time_ms);

    /// @brief Скидання аварійного стану після безпечного розвантаження механіки
    void resetFault() noexcept;

    [[nodiscard]] float getFilteredCurrent() const noexcept { return filtered_current_ma_; }
    [[nodiscard]] float getZeroOffset() const noexcept { return zero_offset_ma_; }
    [[nodiscard]] FaultState getFaultState() const noexcept { return current_fault_; }
    [[nodiscard]] bool isCalibrated() const noexcept { return is_calibrated_; }

private:
    CurrentMonitorConfig config_;
    StallFaultCallback stall_callback_{nullptr};
    void* stall_user_data_{nullptr};
    float zero_offset_ma_{0.0f};
    float filtered_current_ma_{0.0f};
    uint32_t overcurrent_start_ms_{0};
    uint32_t motion_start_ms_{0};
    FaultState current_fault_{FaultState::Normal};
    bool is_calibrated_{false};
    bool in_blanking_window_{false};
};

} // namespace actuator
