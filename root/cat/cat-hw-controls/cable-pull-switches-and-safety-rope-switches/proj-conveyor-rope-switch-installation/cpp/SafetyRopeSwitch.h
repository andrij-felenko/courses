#ifndef SAFETY_ROPE_SWITCH_H
#define SAFETY_ROPE_SWITCH_H

#include <Arduino.h>

/**
 * @brief Перелік станів безпеки двоканального тросового вимикача (IEC 60947-5-5 / ISO 13850)
 */
enum class SafetyState {
    SYSTEM_OK,                  // Робочий стан: обидва канали замкнені (нормальний натяг)
    TRIPPED_ALARM,              // Аварійний стан: спрацювання вимикача (натяг чи обрив троса)
    FAULT_DISCREPANCY,          // Несправність: розбіжність між каналами (контактне зварювання / обрив одного каналу)
    WAITING_FOR_RESET           // Лінія відновлена: очікування свідомого скиду кнопкою Reset
};

/**
 * @brief Структура конфігурації апаратних пінів та часових параметрів
 */
struct SafetyRopeSwitchConfig {
    uint8_t ch1Pin;             // Пін першого каналу NC1
    uint8_t ch2Pin;             // Пін другого каналу NC2
    uint8_t resetPin;           // Пін кнопки скиду Reset
    uint32_t debounceMs;        // Час антибрязкоту у мілісекундах (за замовчуванням 10 мс)
    uint32_t discrepancyTimeoutMs; // Допустимий час розбіжності між каналами (за замовчуванням 50 мс)
};

/**
 * @brief Клас обробки двоканального тросового вимикача з фіксованим станом аварії
 */
class SafetyRopeSwitch {
public:
    explicit SafetyRopeSwitch(const SafetyRopeSwitchConfig& config);

    // Ініціалізація GPIO пінів
    void begin();

    // Неблокуюче опитування стану в циклі loop()
    void update();

    // Запит на скид аварійного стану за кнопкою Reset
    bool reset();

    // Повертає поточний стан системи безпеки
    SafetyState getState() const;

    // Повертає true, якщо система в безпечному робочому стані
    bool isSystemOk() const;

    // Повертає назву поточного стану українською мовою
    const char* getStateName() const;

private:
    SafetyRopeSwitchConfig m_config;
    SafetyState m_state;

    // Стани каналів з антибрязкотом (true = норма/замкнено, false = тривога/відкрито)
    bool m_ch1Raw;
    bool m_ch2Raw;
    bool m_ch1Stable;
    bool m_ch2Stable;

    uint32_t m_ch1LastChangeMs;
    uint32_t m_ch2LastChangeMs;
    uint32_t m_discrepancyStartMs;
    bool m_discrepancyTimingActive;

    // Зчитування та антибрязкіт каналу
    void processDebounce();

    // Перевірка відповідності двох каналів
    void processDiscrepancy();
};

#endif // SAFETY_ROPE_SWITCH_H
