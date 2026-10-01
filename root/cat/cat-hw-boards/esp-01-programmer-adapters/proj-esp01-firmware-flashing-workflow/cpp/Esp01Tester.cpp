#include "Esp01Tester.hpp"

Esp01Tester::Esp01Tester(const UartConfig& uartConf, const GpioConfig& gpioConf)
    : m_uartConfig(uartConf),
      m_gpioConfig(gpioConf),
      m_currentLedState(LedState::Off) {
}

void Esp01Tester::begin() {
    // Ініціалізація послідовного зв'язку UART для Serial Monitor
    Serial.begin(m_uartConfig.baudRate);
    
    // Невелика затримка для стабілізації напрямку ліній UART після скидання
    delay(100);

    // Налаштування GPIO піна світлодіода на вихід
    pinMode(m_gpioConfig.ledPin, OUTPUT);

    // Встановлення початкового стану світлодіода (вимкнений)
    setLedState(LedState::Off);

    Serial.println();
    Serial.println(F("=========================================="));
    Serial.println(F("[ESP-01 Tester] Периферію успішно ініціалізовано."));
    Serial.println(F("=========================================="));
}

void Esp01Tester::writeHardwarePin(LedState state) {
    // Якщо activeLow = true, то увімкнений стан (On) відповідає низькому рівню (LOW)
    if (m_gpioConfig.activeLow) {
        digitalWrite(m_gpioConfig.ledPin, (state == LedState::On) ? LOW : HIGH);
    } else {
        digitalWrite(m_gpioConfig.ledPin, (state == LedState::On) ? HIGH : LOW);
    }
}

void Esp01Tester::setLedState(LedState state) {
    m_currentLedState = state;
    writeHardwarePin(m_currentLedState);
}

void Esp01Tester::toggleLed() {
    if (m_currentLedState == LedState::On) {
        setLedState(LedState::Off);
    } else {
        setLedState(LedState::On);
    }
}

LedState Esp01Tester::getLedState() const {
    return m_currentLedState;
}

void Esp01Tester::printSystemInfo() const {
    Serial.println(F("\n--- СИСТЕМНА ДІАГНОСТИКА МОДУЛЯ ESP-01 ---"));
    
    // Ідентифікатор чіпа ESP8266
    Serial.print(F("ID чіпа ESP8266:        0x"));
    Serial.println(ESP.getChipId(), HEX);

    // Частота тактування процесора Tensilica L106
    Serial.print(F("Тактова частота CPU:   "));
    Serial.print(ESP.getCpuFreqMHz());
    Serial.println(F(" МГц"));

    // Розмір флеш-пам'яті (Flash SPI)
    Serial.print(F("Розмір Flash-пам'яті:  "));
    Serial.print(ESP.getFlashChipSize() / 1024);
    Serial.println(F(" КБ"));

    // Обсяг вільної оперативної пам'яті (SRAM Heap)
    Serial.print(F("Вільна пам'ять (Heap): "));
    Serial.print(ESP.getFreeHeap());
    Serial.println(F(" байт"));

    // Версія SDK від Espressif
    Serial.print(F("Версія Espressif SDK:  "));
    Serial.println(ESP.getSdkVersion());

    // Причина останнього скидання (Reset Reason)
    Serial.print(F("Причина перезавантаження: "));
    Serial.println(ESP.getResetReason());

    // Конфігурація GPIO світлодіода
    Serial.print(F("Пін світлодіода (GPIO): "));
    Serial.print(m_gpioConfig.ledPin);
    Serial.print(F(" (Інверсна логіка Active LOW: "));
    Serial.print(m_gpioConfig.activeLow ? F("ТАК") : F("НІ"));
    Serial.println(F(")"));

    Serial.println(F("------------------------------------------\n"));
}

void Esp01Tester::printHeartbeat(uint32_t cycleCount) const {
    Serial.print(F("[Успіх] Аптайм: "));
    Serial.print(millis() / 1000);
    Serial.print(F(" с | Цикл №"));
    Serial.print(cycleCount);
    Serial.print(F(" | Стан LED: "));
    Serial.println((m_currentLedState == LedState::On) ? F("УВІМКНЕНО") : F("ВИМКНЕНО"));
}
