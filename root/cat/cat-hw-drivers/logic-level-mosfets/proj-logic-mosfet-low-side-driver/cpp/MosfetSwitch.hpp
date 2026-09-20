#ifndef MOSFET_SWITCH_HPP
#define MOSFET_SWITCH_HPP

#include <cstdint>
#include <cstddef>
#include <string_view>

namespace hardware {

/**
 * @brief Перелік підтримувальних транзисторів MOSFET логічного рівня (Logic-Level MOSFETs)
 * @details Логічні MOSFET мають знижений поріг затвора V_GS(th) = 1.0...2.0 В,
 *          що дозволяє їм повністю відкриватися (насичуватися) при логічних рівнях 3.3 В або 5 В МК.
 */
enum class MosfetModel : uint8_t {
    IRLZ44N,  ///< N-Channel, 55V, 47A, Vgs(th)=1.0-2.0V, Rds(on)@5V=0.028 Ohm, Rds(on)@4V=0.039 Ohm
    IRL540N,  ///< N-Channel, 100V, 30A, Vgs(th)=1.0-2.0V, Rds(on)@5V=0.044 Ohm, Rds(on)@4V=0.063 Ohm
    IRL2203N, ///< N-Channel, 30V, 116A, Vgs(th)=1.0V min, Rds(on)@4.5V=0.007 Ohm, Rds(on)@2.8V=0.01 Ohm
    FDD8447L, ///< N-Channel PowerTrench, 40V, 50A, Vgs(th)=1.0-3.0V, Rds(on)@4.5V=0.0105 Ohm
    Custom    ///< Користувацька модель транзистора з власноруч заданими параметрами
};

/**
 * @brief Режими керування силовим ключем MOSFET
 */
enum class ControlMode : uint8_t {
    Disabled,      ///< Ключ вимкнений (затвор притиснутий до GND через pull-down)
    DiscreteGpio,  ///< Дискретне керування (ввімкнено/вимкнено через GPIO)
    HardwarePwm,   ///< Плавна регуляція через апаратний ШІМ МК
    FaultState     ///< Заблокований стан внаслідок аварійного відключення
};

/**
 * @brief Коди помилок та аварійних станів ключа
 */
enum class SwitchFault : uint8_t {
    None = 0,                ///< Штатний режим, помилки відсутні
    NotInitialized,          ///< Спроба виконання операції до безпечної ініціалізації
    DutyCycleExceeded,       ///< Запит робочого циклу ШІМ перевищує встановлений безпечний максимум
    InvalidConfiguration,    ///< Некоректні параметри виводу GPIO або частоти ШІМ
    ThermalLimitReached,     ///< Розрахункове перевищення допустимої температури кристала
    EmergencyStopTriggered   ///< Аварійне негайне вимкнення за зовнішнім сигналом
};

/**
 * @brief Перетворення назви моделі MOSFET у текстовий рядок українською мовою
 */
constexpr std::string_view mosfetModelToString(MosfetModel model) noexcept {
    switch (model) {
        case MosfetModel::IRLZ44N:  return "IRLZ44N (55V, 47A, Logic-Level N-Ch)";
        case MosfetModel::IRL540N:  return "IRL540N (100V, 30A, High-Voltage Logic-Level N-Ch)";
        case MosfetModel::IRL2203N: return "IRL2203N (30V, 116A, Ultra-low Rds(on) Logic-Level)";
        case MosfetModel::FDD8447L: return "FDD8447L (40V, 50A, DPAK PowerTrench Logic-Level)";
        case MosfetModel::Custom:   return "Custom Logic-Level MOSFET";
    }
    return "Невідома модель";
}

/**
 * @brief Перетворення режиму керування у текстовий рядок українською мовою
 */
constexpr std::string_view controlModeToString(ControlMode mode) noexcept {
    switch (mode) {
        case ControlMode::Disabled:     return "Вимкнено (Pull-Down GND)";
        case ControlMode::DiscreteGpio: return "Дискретне керування (GPIO ON/OFF)";
        case ControlMode::HardwarePwm:  return "Апаратний ШІМ (PWM Duty Cycle)";
        case ControlMode::FaultState:   return "Аварійне блокування (Fault)";
    }
    return "Невідомий режим";
}

/**
 * @brief Перетворення коду аварії у текстовий опис українською мовою
 */
constexpr std::string_view switchFaultToString(SwitchFault fault) noexcept {
    switch (fault) {
        case SwitchFault::None:                  return "Норма (помилки відсутні)";
        case SwitchFault::NotInitialized:        return "Система не ініціалізована";
        case SwitchFault::DutyCycleExceeded:     return "Перевищено допустимий робочий цикл ШІМ";
        case SwitchFault::InvalidConfiguration:  return "Помилка конфігурації периферії";
        case SwitchFault::ThermalLimitReached:   return "Перевищено граничну потужність теплорозсіювання";
        case SwitchFault::EmergencyStopTriggered:return "Спрацювала екстрена аварійна зупинка";
    }
    return "Невідома помилка";
}

/**
 * @brief Конфігурація дискретного виводу GPIO МК та підключення затвора
 */
struct PinConfig {
    uint8_t gpioPin{2};             ///< Номер фізичного/логічного виводу GPIO МК
    uint8_t pwmChannel{0};          ///< Номер каналу таймера / апаратного ШІМ
    bool isPwmSupported{true};      ///< Прапорець підтримки апаратного ШІМ даним виводом
    bool activeHigh{true};          ///< Активний рівень сигналу (true = високий рівень відкриває ключ)
    bool internalPullDown{true};    ///< Активація внутрішнього pull-down резистора МК
    uint16_t gateResistorOhms{100}; ///< Опір обмежувального резистора затвора R_G (Ом)
};

/**
 * @brief Налаштування параметрів ШІМ та часових характеристик плавної регуляції
 */
struct PwmConfig {
    uint32_t frequencyHz{5000};     ///< Частота ШІМ у Гц (рекомендовано 1-20 кГц)
    float minDutyPercent{0.0f};     ///< Мінімально припустимий робочий цикл (%)
    float maxDutyPercent{100.0f};   ///< Абсолютний максимум робочого циклу (%)
    float maxSafeDutyPercent{90.0f};///< Захисна межа робочого циклу для збереження ресурсу ключа (%)
    float rampStepPercent{2.0f};    ///< Крок зміни робочого циклу при плавному розгоні (%)
};

/**
 * @brief Електричні й теплові характеристики силового ключа MOSFET
 */
struct MosfetSpecs {
    float maxVoltageV{55.0f};       ///< Гранична напруга сток-витік V_DS (В)
    float maxCurrentA{47.0f};       ///< Граничний струм стоку I_D при T_c=25°C (А)
    float rdsOnOhmsAt3v3{0.035f};   ///< Опір каналу R_DS(on) при V_GS = 3.3 В (Ом)
    float rdsOnOhmsAt5v0{0.028f};   ///< Опір каналу R_DS(on) при V_GS = 5.0 В (Ом)
    float gateChargeNnC{63.0f};     ///< Повний заряд затвора Q_g (нКл)
    float maxPowerDissipationW{2.5f};///< Максимальна розсіювана потужність без радіатора (Вт)
};

/**
 * @brief Поточні робочі метрики та стан модуля керування
 */
struct SwitchMetrics {
    float currentDutyCyclePercent{0.0f}; ///< Поточний значення робочого циклу (%)
    float estimatedCurrentAmpere{0.0f};  ///< Розрахунковий струм навантаження (А)
    float estimatedPowerLossWatts{0.0f}; ///< Розрахункові теплові втрати на MOSFET (Вт)
    uint32_t switchCounter{0};           ///< Кількість переключень (комутацій) ключа
    ControlMode mode{ControlMode::Disabled}; ///< Поточний режим роботи
    SwitchFault lastFault{SwitchFault::None};///< Код останньої помилки/аварії
    bool isEnabled{false};               ///< Прапорець активного стану ключа
};

/**
 * @brief Клас-обгортка для безпечного керування транзисторами MOSFET логічного рівня
 */
class MosfetSwitch {
public:
    MosfetSwitch(MosfetModel model, const PinConfig& pinCfg, const PwmConfig& pwmCfg);

    /**
     * @brief Безпечна ініціалізація периферії МК
     * @details Гарантує початковий стан Pull-Down на затворі для запобігання самовільному
     *          ввімкненню силового ключа під час скидання або завантаження МК.
     * @return true у разі успішного налаштування виводу
     */
    bool initialize();

    /**
     * @brief Дискретне ввімкнення силового ключа (100% duty або прямий High рівень)
     * @return true якщо переключення виконано успішно
     */
    bool turnOn();

    /**
     * @brief Дискретне вимкнення силового ключа (0% duty, Low рівень затвора)
     */
    void turnOff();

    /**
     * @brief Встановлення робочого циклу ШІМ з перевіркою безпечних меж
     * @param dutyPercent Робочий цикл у відсотках [0.0 ... 100.0]
     * @return true якщо значення успішно застосовано
     */
    bool setDutyCycle(float dutyPercent);

    /**
     * @brief Плавна регуляція потужності (Ramp Up/Down) до цільового значення
     * @param targetDutyPercent Цільовий робочий цикл (%)
     * @param stepDelayMs Затримка між кроками наростання (мс)
     * @return true якщо плавний перехід завершено без аварій
     */
    bool smoothRampTo(float targetDutyPercent, uint32_t stepDelayMs = 20);

    /**
     * @brief Аварійне негайне вимкнення ключа з переходом у стан FaultState
     * @param reason Причина аварійного зупину
     */
    void emergencyShutdown(SwitchFault reason = SwitchFault::EmergencyStopTriggered);

    /**
     * @brief Скидання аварійного стану після усунення несправності
     * @return true якщо систему повернуто у нормальний вимкнений стан
     */
    bool clearFault();

    /**
     * @brief Оновлення розрахункового струму навантаження для моніторингу нагріву
     * @param loadCurrentA Струм навантаження у колі стоку (А)
     * @param gateVoltageV Напруга на затворі V_GS (3.3 В або 5.0 В)
     */
    void updateLoadEstimates(float loadCurrentA, float gateVoltageV = 3.3f);

    /**
     * @brief Отримання повної оперативної інформації про стан ключа
     */
    [[nodiscard]] SwitchMetrics getMetrics() const;

    /**
     * @brief Перевірка чи відкритий силовий ключ
     */
    [[nodiscard]] bool isEnabled() const noexcept { return m_isEnabled; }

    /**
     * @brief Отримання обраної моделі MOSFET
     */
    [[nodiscard]] MosfetModel getModel() const noexcept { return m_model; }

    /**
     * @brief Отримання технічних специфікацій транзистора
     */
    [[nodiscard]] MosfetSpecs getSpecs() const noexcept { return m_specs; }

private:
    void applyHardwarePinState(bool state);
    void applyHardwarePwmDuty(float dutyPercent);
    static MosfetSpecs lookupSpecs(MosfetModel model);

    MosfetModel m_model;
    PinConfig m_pinCfg;
    PwmConfig m_pwmCfg;
    MosfetSpecs m_specs;

    bool m_initialized{false};
    bool m_isEnabled{false};

    float m_currentDutyPercent{0.0f};
    float m_estimatedCurrentA{0.0f};
    float m_estimatedPowerLossW{0.0f};
    uint32_t m_switchCounter{0};

    ControlMode m_mode{ControlMode::Disabled};
    SwitchFault m_lastFault{SwitchFault::None};
};

} // namespace hardware

#endif // MOSFET_SWITCH_HPP
