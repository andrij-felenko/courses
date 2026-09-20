#pragma once

#include <Arduino.h>

// Конфігурація підключення ліній BCD та вибору декад
struct BcdPinConfig {
    uint8_t pinBit1; // Сигнальна лінія BCD біта 1 (вага 1)
    uint8_t pinBit2; // Сигнальна лінія BCD біта 2 (вага 2)
    uint8_t pinBit4; // Сигнальна лінія BCD біта 4 (вага 4)
    uint8_t pinBit8; // Сигнальна лінія BCD біта 8 (вага 8)
    
    const uint8_t* digitEnablePins; // Масив пінів активації декад (для мультиплексування)
    uint8_t digitCount;             // Кількість декадних барабанів
    
    uint16_t debounceMs; // Інтервал фільтрації брязкоту контактів (мс)
};

class ThumbwheelBcd {
public:
    explicit ThumbwheelBcd(const BcdPinConfig& config);
    ~ThumbwheelBcd();

    // Ініціалізація GPIO-пінів мікроконтролера
    void begin();

    // Неблокувальне сканування входів (виклики у циклі loop)
    void update();

    // Отримання зчитаного числового значення
    uint32_t getValue() const;

    // Перевірка прапорця оновлення уставки
    bool hasChanged();

private:
    uint8_t readRawNibble(uint8_t digitIndex);

    BcdPinConfig m_config;
    uint32_t m_currentValue{0};
    uint32_t m_pendingValue{0};
    uint32_t m_lastDebounceTime{0};
    bool m_hasChanged{false};
};
