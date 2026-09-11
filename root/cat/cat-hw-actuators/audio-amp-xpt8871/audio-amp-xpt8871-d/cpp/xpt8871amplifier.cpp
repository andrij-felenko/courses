// Драйвер керування XPT8871 мовою C++ (об'єктноорієнтований інтерфейс для Arduino / STM32 / RP2040)
#include <Arduino.h>

class XPT8871Amplifier {
public:
    explicit XPT8871Amplifier(uint8_t shdn_pin, uint16_t wakeup_delay_ms = 150)
        : m_pin(shdn_pin), m_delay_ms(wakeup_delay_ms), m_active(false) {}

    void begin() {
        // Гарантуємо високий рівень з першої миті ініціалізації
        pinMode(m_pin, OUTPUT);
        digitalWrite(m_pin, HIGH);
        m_active = false;
    }

    void wake() {
        if (m_active) {
            return;
        }

        // Чекаємо, доки внутрішнє коло BYPASS стабілізує віртуальну землю
        delay(m_delay_ms);

        // Переводимо SHDN у низький рівень — виходи переходять у робочий режим
        digitalWrite(m_pin, LOW);
        m_active = true;
    }

    void sleep() {
        if (!m_active) {
            return;
        }

        // Блокуємо силові каскади — споживання падає нижче 1 мкА
        digitalWrite(m_pin, HIGH);
        m_active = false;
    }

    bool isActive() const {
        return m_active;
    }

private:
    uint8_t m_pin;
    uint16_t m_delay_ms;
    bool m_active;
};
