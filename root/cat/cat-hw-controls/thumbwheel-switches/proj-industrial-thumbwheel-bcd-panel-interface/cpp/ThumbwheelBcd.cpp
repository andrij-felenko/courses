#include "ThumbwheelBcd.h"

ThumbwheelBcd::ThumbwheelBcd(const BcdPinConfig& config)
    : m_config(config) {
}

ThumbwheelBcd::~ThumbwheelBcd() = default;

void ThumbwheelBcd::begin() {
    // Налаштування вхідних ліній BCD з внутрішнім підтягуванням
    pinMode(m_config.pinBit1, INPUT_PULLUP);
    pinMode(m_config.pinBit2, INPUT_PULLUP);
    pinMode(m_config.pinBit4, INPUT_PULLUP);
    pinMode(m_config.pinBit8, INPUT_PULLUP);

    // Налаштування ліній активації декад (виходи керування)
    if (m_config.digitEnablePins != nullptr) {
        for (uint8_t i = 0; i < m_config.digitCount; ++i) {
            pinMode(m_config.digitEnablePins[i], OUTPUT);
            digitalWrite(m_config.digitEnablePins[i], HIGH); // Деактивація (активний LOW)
        }
    }
}

uint8_t ThumbwheelBcd::readRawNibble(uint8_t digitIndex) {
    // Якщо використовується мультиплексування — активуємо потрібну декаду
    if (m_config.digitEnablePins != nullptr) {
        digitalWrite(m_config.digitEnablePins[digitIndex], LOW);
        delayMicroseconds(5); // Коротке вирівнювання сигналу на лінії
    }

    // Зчитування стану 4 бітів (інвертуємо при INPUT_PULLUP та активному низькому рівні ламелей)
    uint8_t b1 = (digitalRead(m_config.pinBit1) == LOW) ? 1 : 0;
    uint8_t b2 = (digitalRead(m_config.pinBit2) == LOW) ? 1 : 0;
    uint8_t b4 = (digitalRead(m_config.pinBit4) == LOW) ? 1 : 0;
    uint8_t b8 = (digitalRead(m_config.pinBit8) == LOW) ? 1 : 0;

    // Деактивуємо декаду після зчитування
    if (m_config.digitEnablePins != nullptr) {
        digitalWrite(m_config.digitEnablePins[digitIndex], HIGH);
    }

    uint8_t nibble = (b8 << 3) | (b4 << 2) | (b2 << 1) | b1;
    return nibble;
}

void ThumbwheelBcd::update() {
    uint32_t now = millis();

    // Сканування всіх декад та формування проміжного значення
    uint32_t rawCalculatedValue = 0;
    uint32_t multiplier = 1;
    bool isValidBcd = true;

    for (uint8_t i = 0; i < m_config.digitCount; ++i) {
        uint8_t digit = readRawNibble(i);

        // Перевірка на невалідні коди (10..15) під час механічного перемикання ламелей
        if (digit > 9) {
            isValidBcd = false;
            break;
        }

        rawCalculatedValue += digit * multiplier;
        multiplier *= 10;
    }

    // Якщо зчитаний BCD-код невалідний — ігноруємо цей такт (триває брязкіт/перехід)
    if (!isValidBcd) {
        m_lastDebounceTime = now;
        return;
    }

    // Алгоритм програмного дебаунсу для стабільних станів
    if (rawCalculatedValue != m_pendingValue) {
        m_pendingValue = rawCalculatedValue;
        m_lastDebounceTime = now;
    } else {
        if ((now - m_lastDebounceTime) >= m_config.debounceMs) {
            if (m_currentValue != m_pendingValue) {
                m_currentValue = m_pendingValue;
                m_hasChanged = true;
            }
        }
    }
}

uint32_t ThumbwheelBcd::getValue() const {
    return m_currentValue;
}

bool ThumbwheelBcd::hasChanged() {
    if (m_hasChanged) {
        m_hasChanged = false;
        return true;
    }
    return false;
}
