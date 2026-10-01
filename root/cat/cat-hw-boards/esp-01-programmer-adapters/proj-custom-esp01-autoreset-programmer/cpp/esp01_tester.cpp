#include "esp01_tester.hpp"
#include <ESP8266WiFi.h>

LedIndicator::LedIndicator(uint8_t pin, bool activeLow)
    : m_pin(pin), m_activeLow(activeLow), m_state(false) {}

void LedIndicator::begin() {
    pinMode(m_pin, OUTPUT);
    turnOff();
}

void LedIndicator::turnOn() {
    m_state = true;
    digitalWrite(m_pin, m_activeLow ? LOW : HIGH);
}

void LedIndicator::turnOff() {
    m_state = false;
    digitalWrite(m_pin, m_activeLow ? HIGH : LOW);
}

void LedIndicator::toggle() {
    if (m_state) {
        turnOff();
    } else {
        turnOn();
    }
}

void LedIndicator::blink(unsigned int durationMs, unsigned int count) {
    for (unsigned int i = 0; i < count; ++i) {
        turnOn();
        delay(durationMs);
        turnOff();
        if (i + 1 < count) {
            delay(durationMs);
        }
    }
}

bool LedIndicator::isOn() const {
    return m_state;
}

Esp01Tester::Esp01Tester(uint8_t ledPin, bool activeLow)
    : m_led(ledPin, activeLow), m_lastUpdateMs(0), m_heartbeatCount(0) {}

void Esp01Tester::begin(unsigned long baudRate) {
    m_led.begin();
    Serial.begin(baudRate);
    
    // Невелика затримка для стабілізації UART після автоскидання DTR/RTS
    delay(500);

    Serial.println();
    Serial.println(F("=========================================="));
    Serial.println(F("   ESP-01 Programmer Verification Test    "));
    Serial.println(F("=========================================="));

    printChipDiagnostics();

    // Серія швидких спалахів світлодіода підтверджує старт після скидання
    m_led.blink(80, 5);
}

void Esp01Tester::printChipDiagnostics() {
    Serial.println(F("[INFO] Результати автотестування чипа ESP8266:"));
    
    // Частота процесора
    Serial.print(F("  - Частота CPU:           "));
    Serial.print(ESP.getCpuFreqMHz());
    Serial.println(F(" МГц"));

    // Ідентифікатори та розміри пам'яті
    Serial.print(F("  - Chip ID:               0x"));
    Serial.println(ESP.getChipId(), HEX);

    Serial.print(F("  - Flash Chip ID:         0x"));
    Serial.println(ESP.getFlashChipId(), HEX);

    Serial.print(F("  - Обсяг Flash пам'яті:   "));
    Serial.print(ESP.getFlashChipRealSize() / 1024);
    Serial.println(F(" КБ"));

    Serial.print(F("  - Вільний обсяг Heap:    "));
    Serial.print(ESP.getFreeHeap());
    Serial.println(F(" байт"));

    // МАС-адреса Wi-Fi адаптера
    Serial.print(F("  - MAC-адреса модуля:     "));
    Serial.println(WiFi.macAddress());

    // Причина останнього перезавантаження (Reset Reason)
    Serial.print(F("  - Причина скидання:      "));
    Serial.println(ESP.getResetReason());

    Serial.println(F("=========================================="));
    Serial.println(F("[OK] Автоматичне завантаження прошивки DTR/RTS пройдено успішно!"));
}

void Esp01Tester::update() {
    unsigned long currentMs = millis();
    // Періодичне миготіння індикатора кожну секунду (Heartbeat)
    if (currentMs - m_lastUpdateMs >= 1000) {
        m_lastUpdateMs = currentMs;
        m_heartbeatCount++;
        m_led.toggle();

        Serial.print(F("[HEARTBEAT] Час роботи: "));
        Serial.print(currentMs / 1000);
        Serial.print(F(" с | Статус світлодіода: "));
        Serial.println(m_led.isOn() ? F("УВІМК") : F("ВИМК"));
    }
}
