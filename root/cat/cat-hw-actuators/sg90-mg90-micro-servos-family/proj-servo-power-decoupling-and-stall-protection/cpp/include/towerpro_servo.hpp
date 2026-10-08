#ifndef TOWERPRO_SERVO_HPP
#define TOWERPRO_SERVO_HPP

#include "pwm_driver.hpp"
#include "adc_current_sensor.hpp"
#include <functional>
#include <cstdint>

namespace towerpro {

/**
 * @brief Перелічення моделей 9-грамових мікросервоприводів Tower Pro.
 */
enum class ServoModel {
    SG90,   ///< Пластикові шестерні, аналоговий (струм заклинювання ~650 мА)
    SG92R,  ///< Вуглепластикові шестерні, аналоговий (струм заклинювання ~750 мА)
    MG90S,  ///< Металеві шестерні, аналоговий (струм заклинювання ~900 мА)
    MG90D   ///< Металеві шестерні, цифровий (струм заклинювання ~1200 мА)
};

/**
 * @brief Апаратний профіль специфічних характеристик моделі.
 */
struct ServoProfile {
    const char* modelName;
    uint16_t minPulseUs;              ///< Мінімальна тривалість імпульсу (0°)
    uint16_t maxPulseUs;              ///< Максимальна тривалість імпульсу (180°)
    float maxAngleDeg;                ///< Максимальний кут позиціонування
    float stallCurrentThresholdmA;    ///< Поріг перевантаження за струмом (мА)
    uint32_t stallTimeoutMs;          ///< Крітичний час перевантаження до аварійного зупину (мс)
    bool isDigital;                   ///< Тип контролера (цифровий/аналоговий)
    bool isMetalGear;                 ///< Матеріал шестерень (метал/пластик)
};

/**
 * @brief Конфігурація сервоприводу.
 */
struct ServoConfig {
    ServoModel model{ServoModel::SG90};
    uint8_t pwmPin{9};
    AdcSensorConfig adcConfig{};

    // Перевизначення параметрів за замовчуванням (0 - вимикає перевизначення)
    uint16_t overrideMinPulseUs{0};
    uint16_t overrideMaxPulseUs{0};
    float overrideStallCurrentLimitmA{0.0f};
    uint32_t overrideStallTimeoutMs{0};
};

/**
 * @brief Зворотний виклик при виникненні аварійного заклинювання/перевантаження.
 */
using EmergencyCallback = std::function<void(ServoModel model, float currentmA, uint32_t overloadDurationMs)>;

/**
 * @brief Високорівневий C++ клас для керування сервоприводами Tower Pro із захистом від перевантажень.
 */
class TowerProServo {
public:
    TowerProServo() = default;

    /**
     * @brief Отримати апаратний профіль за замовчуванням для заданої моделі.
     */
    static ServoProfile getProfile(ServoModel model);

    /**
     * @brief Ініціалізація сервоприводу та струмового моніторингу.
     * @param config Структура з налаштуваннями.
     * @return true у разі успішного старту.
     */
    bool begin(const ServoConfig& config);

    /**
     * @brief Встановити цільовий кут у градусах (0..maxAngleDeg).
     */
    void setAngle(float degrees);

    /**
     * @brief Отримати поточний кут у градусах.
     */
    float getAngle() const;

    /**
     * @brief Встановити тривалість ШІМ-імпульсу у мікросекундах.
     */
    void writeMicroseconds(uint16_t pulseUs);

    /**
     * @brief Зчитати поточну тривалість імпульсу ШІМ.
     */
    uint16_t readMicroseconds() const;

    /**
     * @brief Неблокуюче оновлення стану, опитування АЦП та перевірка струмового ліміту.
     * @param currentTimeMs Поточний системний час у мілісекундах.
     * @param currentTimeUs Поточний системний час у мікросекундах.
     */
    void update(uint32_t currentTimeMs, uint32_t currentTimeUs);

    /**
     * @brief Відключити ШІМ-сигнал.
     */
    void detach();

    /**
     * @brief Відновити ШІМ-сигнал.
     */
    void attach();

    /**
     * @brief Перевірити, чи подається ШІМ.
     */
    bool isAttached() const;

    /**
     * @brief Чи зафіксовано поточне перевантаження за струмом.
     */
    bool isOverloaded() const;

    /**
     * @brief Чи активовано аварійну зупинку (Emergency Stop).
     */
    bool isEmergencyStopped() const;

    /**
     * @brief Скинути стан аварійної зупинки та відновити роботу.
     */
    void resetEmergency();

    /**
     * @brief Зареєструвати функцію зворотного виклику аварійного зупину.
     */
    void setEmergencyCallback(EmergencyCallback callback);

    /**
     * @brief Отримати поточний відфільтрований струм споживання (мА).
     */
    float getCurrentmA() const;

    /**
     * @brief Встановити симульоване значення АЦП для тестування захисту.
     */
    void setSimulatedAdcRaw(uint16_t adcRaw);

    /**
     * @brief Отримати активний профіль сервоприводу.
     */
    const ServoProfile& getActiveProfile() const { return profile_; }

private:
    PwmDriver pwmDriver_;
    AdcCurrentSensor currentSensor_;
    ServoProfile profile_{};
    ServoConfig config_{};
    
    float targetAngleDeg_{90.0f};
    uint16_t currentPulseUs_{1500};
    
    bool emergencyStopped_{false};
    bool overloaded_{false};
    uint32_t overloadStartTimeMs_{0};
    uint32_t currentOverloadDurationMs_{0};

    EmergencyCallback emergencyCallback_{nullptr};

    uint16_t angleToMicroseconds(float angle) const;
    float microsecondsToAngle(uint16_t pulseUs) const;
};

} // namespace towerpro

#endif // TOWERPRO_SERVO_HPP
