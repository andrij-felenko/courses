#ifndef ESC_CONTROL_HPP
#define ESC_CONTROL_HPP

#include <cstdint>
#include <algorithm>
#include <string_view>

namespace esc {

/**
 * @brief Перелічення станів стабільності вихідної напруги лінійки BEC.
 */
enum class BecStatus : uint8_t {
    Ok = 0,     ///< Напруга BEC у нормі (>= 4.75 В)
    Warning,    ///< Попередження про просідання (4.50 В .. 4.75 В)
    Critical    ///< Аварійне просідання (< 4.50 В), потрібен захист
};

/**
 * @brief Клас інкапсуляції керування ESC BLHeli та апаратного моніторингу BEC.
 */
class EscController {
public:
    /* Параметри керуючого ШІМ-сигналу */
    static constexpr uint16_t kMinPulseUs = 1000;
    static constexpr uint16_t kMaxPulseUs = 2000;
    static constexpr uint16_t kNeutralPulseUs = 1000;
    static constexpr uint32_t kPwmFrequencyHz = 50;
    static constexpr uint32_t kPwmPeriodUs = 20000;

    /* Параметри АЦП та дільника напруги */
    static constexpr float kVrefVolts = 3.3f;
    static constexpr float kAdcMaxVal = 4095.0f; // 12-бітний АЦП
    static constexpr float kResistorR1Ohms = 10000.0f;
    static constexpr float kResistorR2Ohms = 10000.0f;
    static constexpr float kDividerRatio = (kResistorR1Ohms + kResistorR2Ohms) / kResistorR2Ohms;

    /* Поріг виявлення несправностей BEC */
    static constexpr float kBecNominalVolts = 5.00f;
    static constexpr float kBecWarnVolts = 4.75f;
    static constexpr float kBecCritVolts = 4.50f;

    EscController() noexcept = default;
    ~EscController() noexcept = default;

    // Заборона копіювання для запобігання дублюванню апаратного контролю
    EscController(const EscController&) = delete;
    EscController& operator=(const EscController&) = delete;
    EscController(EscController&&) noexcept = default;
    EscController& operator=(EscController&&) noexcept = default;

    /**
     * @brief Ініціалізація апаратних таймерів ШІМ, АЦП та армування регулятора.
     */
    void init();

    /**
     * @brief Встановлення тривалості імпульсу керування дроселем.
     * @param pulse_us Тривалість імпульсу у мікросекундах (1000..2000).
     * @return true Якщо газ встановлено успішно, false якщо активне блокування.
     */
    bool setThrottle(uint16_t pulse_us);

    /**
     * @brief Перерахунок сирого значення АЦП у напругу лінії BEC.
     * @param raw_adc Сирий відлік АЦП (0..4095).
     * @return float Напруга в вольтах.
     */
    [[nodiscard]] constexpr float convertAdcToVoltage(uint16_t raw_adc) const noexcept {
        const float v_pin = (static_cast<float>(raw_adc) * kVrefVolts) / kAdcMaxVal;
        return v_pin * kDividerRatio;
    }

    /**
     * @brief Перевірка та оновлення стану BEC за виміряним АЦП.
     * @param raw_adc Сире значення АЦП.
     * @return BecStatus Поточний статус лінії BEC.
     */
    BecStatus updateBecMonitoring(uint16_t raw_adc);

    /**
     * @brief Циклічна обробка контролю живлення та оновлення ШІМ.
     * @param raw_adc Сире значення АЦП.
     * @param target_pulse_us Запитана ширина імпульсу.
     */
    void process(uint16_t raw_adc, uint16_t target_pulse_us);

    // Геттери стану
    [[nodiscard]] uint16_t getPulseWidthUs() const noexcept { return current_pulse_us_; }
    [[nodiscard]] float getBecVoltage() const noexcept { return bec_voltage_; }
    [[nodiscard]] BecStatus getStatus() const noexcept { return status_; }
    [[nodiscard]] bool isArmed() const noexcept { return is_armed_; }
    [[nodiscard]] bool isEmergencyStop() const noexcept { return emergency_stop_; }
    [[nodiscard]] static std::string_view statusToString(BecStatus status) noexcept;

private:
    void initHardwarePeripherals();
    void writePwmHardware(uint16_t pulse_us);

    uint16_t current_pulse_us_{kNeutralPulseUs};
    float bec_voltage_{kBecNominalVolts};
    BecStatus status_{BecStatus::Ok};
    bool is_armed_{false};
    bool emergency_stop_{false};
};

} // namespace esc

#endif // ESC_CONTROL_HPP
