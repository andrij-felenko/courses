#pragma once

#include <cstdint>
#include <functional>
#include "moving_average_filter.hpp"

/**
 * @brief Режим роботи контролера рівня рідини.
 */
enum class ControlMode {
    Fill,  ///< Режим підкачування (наповнення): насос вмикається при низькому рівні та вимикається при високому
    Drain  ///< Режим осушення (зливання): насос вмикається при високому рівні та вимикається при низькому
};

/**
 * @brief Структура порогових значень рівня рідини з гістерезисом.
 */
struct LevelThresholds {
    float lowThreshold;   ///< Нижній поріг (у відсотках 0-100%)
    float highThreshold;  ///< Верхній поріг (у відсотках 0-100%)
};

/**
 * @brief Структура конфігураційних параметрів контролера.
 */
struct ControllerConfig {
    uint8_t pinExcitationA;       ///< Пін A для імпульсу збудження (полярність +)
    uint8_t pinExcitationB;       ///< Пін B для імпульсу збудження (полярність -)
    uint8_t pinAnalogRead;        ///< Аналоговий пін для зчитування падіння напруги
    uint8_t pinRelay;             ///< Цифровий пін керування силовим реле насоса
    LevelThresholds thresholds;   ///< Порогові значення рівня рідини
    ControlMode mode;             ///< Режим роботи: Fill (наповнення) або Drain (зливання)
    std::size_t filterWindowSize; ///< Розмір вікна цифрового фільтра ковзного середнього
    uint16_t pulseDelayUs;        ///< Затримка імпульсу збудження у мікросекундах
    bool activeLowRelay;          ///< Прапорець інверсії логіки реле (true — активний низький рівень)
};

/**
 * @brief Типи функцій-адаптерів для абстрагування апаратного периферійного рівня (GPIO / ADC).
 */
using DigitalWriteFn = std::function<void(uint8_t pin, bool state)>;
using AnalogReadFn = std::function<uint16_t(uint8_t pin)>;
using DelayUsFn = std::function<void(uint16_t microseconds)>;

/**
 * @brief Клас LiquidLevelController для автоматизованого керування рівнем рідини.
 * 
 * Інкапсулює:
 * 1. Генерацію короткочасних прямокутних імпульсів змінної полярності для захисту занурених електродів від електролізу.
 * 2. Цифрову фільтрацію згладжуванням шумів та хвильових коливань поверхні рідини.
 * 3. Логіку порогового регулювання реле з гістерезисом для захисту насосного обладнання від частих перемикань.
 */
class LiquidLevelController {
public:
    /**
     * @brief Конструктор контролера рівня рідини.
     * @param config Структура з апаратними та логічними параметрами.
     * @param dwFunc Апаратна функція цифрового запису (digitalWrite).
     * @param arFunc Апаратна функція аналогового зчитування (analogRead).
     * @param delayUsFunc Апаратна функція затримки у мікросекундах (delayMicroseconds).
     */
    LiquidLevelController(const ControllerConfig& config,
                           DigitalWriteFn dwFunc,
                           AnalogReadFn arFunc,
                           DelayUsFn delayUsFunc);

    /**
     * @brief Ініціалізація периферійних пінів та початкового стану контролера.
     */
    void begin();

    /**
     * @brief Виконати один цикл вимірювання та оновлення стану регулювального реле.
     * @return Поточне фільтроване значення рівня рідини.
     */
    float update();

    /**
     * @brief Отримати останнє обчислене фільтроване значення рівня.
     */
    float getFilteredLevel() const;

    /**
     * @brief Перевірити поточний активний стан силового реле.
     * @return true, якщо реле включене (насос працює), false — якщо вимкнене.
     */
    bool isRelayActive() const;

    /**
     * @brief Отримати поточну конфігурацію контролера.
     */
    const ControllerConfig& getConfig() const;

    /**
     * @brief Динамічне оновлення порогових значень гістерезису.
     * @param low Нижній поріг.
     * @param high Верхній поріг.
     */
    void setThresholds(float low, float high);

    /**
     * @brief Зміна режиму роботи контролера (Fill / Drain).
     */
    void setControlMode(ControlMode mode);

private:
    /**
     * @brief Зчитування сирого значення аналогового сигналу з подачею імпульсів проти електролізу.
     * @return Зчитана напруга або відносне значення у відсотках.
     */
    float readRawSensorExcited();

    /**
     * @brief Оновлення стану реле на основі фільтрованого рівня та логіки гістерезису.
     * @param currentLevel Поточне фільтроване значення рівня.
     */
    void updateRelayState(float currentLevel);

    /**
     * @brief Перемикання виходу реле відповідно до апаратної полярності (Active HIGH / Active LOW).
     * @param active Стан реле (true = увімкнено, false = вимкнено).
     */
    void setRelayOutput(bool active);

    ControllerConfig config_;
    MovingAverageFilter filter_;
    DigitalWriteFn digitalWrite_;
    AnalogReadFn analogRead_;
    DelayUsFn delayUs_;

    float lastFilteredLevel_;
    bool relayActive_;
    bool initialized_;
};
