#ifndef ESP01_TESTER_HPP
#define ESP01_TESTER_HPP

#include <Arduino.h>

// Клас LedIndicator інкапсулює низькорівневе керування GPIO
// бортового світлодіода модуля ESP-01 з урахуванням інвертованої (Active-Low) логіки.
class LedIndicator {
public:
    explicit LedIndicator(uint8_t pin = 2, bool activeLow = true);

    // Ініціалізація виводу мікроконтролера в режим виходу
    void begin();

    // Увімкнення світлодіода
    void turnOn();

    // Вимкнення світлодіода
    void turnOff();

    // Зміна стану світлодіода на протилежний
    void toggle();

    // Генерація кількох спалахів з заданим інтервалом
    void blink(unsigned int durationMs, unsigned int count = 1);

    // Перевірка поточного стану індикатора
    bool isOn() const;

private:
    uint8_t m_pin;
    bool m_activeLow;
    bool m_state;
};

// Клас Esp01Tester відповідає за збір системної інформації чипа ESP8266
// та верифікацію успішного автоматичного скидання (DTR/RTS) через програматор.
class Esp01Tester {
public:
    explicit Esp01Tester(uint8_t ledPin = 2, bool activeLow = true);

    // Ініціалізація послідовного порту та вивід діагностичної інформації чипа
    void begin(unsigned long baudRate = 115200);

    // Оновлення стану тестової програми у головному циклі (heartbeat)
    void update();

    // Друк розширеної системної інформації мікроконтролера ESP8266
    void printChipDiagnostics();

private:
    LedIndicator m_led;
    unsigned long m_lastUpdateMs;
    unsigned int m_heartbeatCount;
};

#endif // ESP01_TESTER_HPP
