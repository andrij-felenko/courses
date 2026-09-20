#ifndef APC_LASER_CONTROLLER_HPP
#define APC_LASER_CONTROLLER_HPP

#include <cstdint>
#include <array>
#include <cstddef>
#include <string_view>

namespace laser {

/**
 * @brief Причини виникнення аварійних станів драйвера
 */
enum class FaultReason : uint8_t {
    None = 0,               ///< Робота в нормі, помилки відсутні
    OverTemperature,        ///< Перевищення максимальної робочої температури
    UnderTemperature,       ///< Температура нижча допустимого мінімуму
    CriticalOverTemperature,///< Досягнення критичної температури (негайне відключення)
    OverCurrent,            ///< Струм накачки перевищує заданий ліміт
    MpdOpenCircuit,         ///< Обрив або відсутність сигналу з моніторного фотодіода
    CodProtectionTriggered  ///< Загроза катастрофічного оптичного пошкодження кристала (COD)
};

/**
 * @brief Перетворення коду аварії у текстовий опис українською мовою
 */
constexpr std::string_view faultReasonToString(FaultReason reason) noexcept {
    switch (reason) {
        case FaultReason::None:                    return "Норма (без помилок)";
        case FaultReason::OverTemperature:         return "Перевищення робочої температури";
        case FaultReason::UnderTemperature:        return "Переохолодження кристала";
        case FaultReason::CriticalOverTemperature: return "Критичний перегрів кристала";
        case FaultReason::OverCurrent:             return "Перевищення струму накачки";
        case FaultReason::MpdOpenCircuit:          return "Обрив кола моніторного фотодіода (APC)";
        case FaultReason::CodProtectionTriggered:  return "Спрацював захист від COD (оптичний пробій)";
    }
    return "Невідома помилка";
}

/**
 * @brief Конфігурація струму накачки та параметрів лазерного діода
 */
struct CurrentConfig {
    float maxPumpCurrentmA{150.0f};   ///< Максимально припустимий струм накачки I_max (мА)
    float thresholdCurrentmA{25.0f};  ///< Поріг генерації лазерного випромінювання I_th (мА)
    float targetPowerMW{5.0f};        ///< Бажана оптична потужність P_out (мВт)
    float slopeEfficiency{0.40f};     ///< Диференційна оптична ефективність dP/dI (мВт/мА)
    float mpdResponsivity{0.20f};     ///< Чутливість моніторного фотодіода S_mpd (мкА/мВт)
};

/**
 * @brief Межі температурного захисту модуля
 */
struct ThermalConfig {
    float minTempCelsius{10.0f};      ///< Мінімальна температура експлуатації (°C)
    float maxTempCelsius{50.0f};      ///< Максимальна робоча температура (°C)
    float criticalTempCelsius{60.0f}; ///< Критична межа перегріву для спасіння кристала (°C)
};

/**
 * @brief Поточні операційні метрики та стан драйвера
 */
struct ApcMetrics {
    float currentPumpmA{0.0f};         ///< Фактичний струм накачки (мА)
    float opticalPowerMW{0.0f};        ///< Обчислена оптична потужність (мВт)
    float mpdCurrentuA{0.0f};          ///< Струм зворотного зв'язку з фотодіода (мкА)
    float temperatureCelsius{25.0f};   ///< Температура корпусу/кристала (°C)
    float powerStabilityPercent{0.0f}; ///< Оцінка стабільності випромінювання (%)
    bool isLaserEnabled{false};        ///< Стан силового каскаду випромінювача
    FaultReason lastFault{FaultReason::None}; ///< Код останньої помилки
};

/**
 * @brief Клас керування драйвером лазерного діода з аналогово-цифровим контуром APC
 */
class ApcLaserController {
public:
    static constexpr std::size_t STABILITY_WINDOW_SIZE = 10;

    ApcLaserController(const CurrentConfig& currentCfg, const ThermalConfig& thermalCfg);

    /**
     * @brief Ініціалізація системних ресурсів та первинний контроль параметрів
     * @return true у разі успішної ініціалізації
     */
    bool initialize();

    /**
     * @brief Безпечний плавний запуск лазера (Soft-Start)
     * @return true якщо плавну подачу струму виконано успішно
     */
    bool enableLaser();

    /**
     * @brief Аварійне або контрольоване вимкнення лазера
     * @param reason Причина вимкнення
     */
    void disableLaser(FaultReason reason = FaultReason::None);

    /**
     * @brief Один крок обробки аналогово-цифрового контуру APC
     * @param deltaTimeSec Час, що минув з попередньої ітерації (секунди)
     */
    void processControlLoop(float deltaTimeSec);

    /**
     * @brief Програмування нової уставної оптичної потужності
     * @param powerMW Цільова потужність у мВт
     */
    bool setTargetPower(float powerMW);

    /**
     * @brief Оновлення виміряної температури від НТК-сенсора
     * @param tempCelsius Температура у градусах Цельсія
     */
    void updateTemperatureSensor(float tempCelsius);

    /**
     * @brief Оновлення зчитаного з АЦП струму моніторного фотодіода
     * @param mpdCurrentuA Струм фотодіода у мкА
     */
    void updatePhotodiodeSensor(float mpdCurrentuA);

    /**
     * @brief Отримання зведеного звіту метрик контролера
     */
    [[nodiscard]] ApcMetrics getMetrics() const;

    /**
     * @brief Перевірка чи активний силовий драйвер
     */
    [[nodiscard]] bool isEnabled() const noexcept { return m_isEnabled; }

    /**
     * @brief Скидання аварійного стану
     */
    void clearFault();

private:
    void hwSetPumpCurrent(float currentmA);
    void hwEmergencyShutdown();
    void updateStabilityCalculation(float currentPower);
    bool checkSafetyLimits();

    CurrentConfig m_currentCfg;
    ThermalConfig m_thermalCfg;

    bool m_initialized{false};
    bool m_isEnabled{false};

    float m_targetPowerMW{0.0f};
    float m_actualPumpCurrentmA{0.0f};
    float m_measuredPowerMW{0.0f};
    float m_measuredMpdCurrentuA{0.0f};
    float m_temperatureCelsius{25.0f};
    float m_powerStabilityPercent{100.0f};

    FaultReason m_currentFault{FaultReason::None};

    std::array<float, STABILITY_WINDOW_SIZE> m_powerHistory{};
    std::size_t m_historyIndex{0};
    std::size_t m_historyCount{0};
};

} // namespace laser

#endif // APC_LASER_CONTROLLER_HPP
