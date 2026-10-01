#include "EspModuleController.hpp"

EspModuleController::EspModuleController(ModuleRevision revision, UartConfig uartConf)
    : m_revision(revision),
      m_uartConfig(uartConf),
      m_ledConfig{},
      m_ledState(false)
{
    // Визначення GPIO та параметрів інверсії світлодіода відповідно до ревізії
    if (m_revision == ModuleRevision::Esp01) {
        // У класичному ESP-01 синій світлодіод підключений до GPIO1 (TXD)
        // Інвертована логіка: катод на GPIO1, анод через резистор до VCC (3.3V)
        m_ledConfig.gpioPin = 1; // GPIO1 / TXD
        m_ledConfig.activeLow = true;
    } else {
        // В ESP-01S синій світлодіод перенесено на GPIO2
        // Інвертована логіка: 0 вмикає світлодіод, 1 вимикає
        m_ledConfig.gpioPin = 2; // GPIO2
        m_ledConfig.activeLow = true;
    }
}

void EspModuleController::begin() {
    // Ініціалізація послідовного зв'язку UART
    Serial.begin(m_uartConfig.baudRate);
    
    // Коротке очікування для стабілізації UART після скидання
    delay(100);

    // Налаштування напрямку роботи виводу GPIO світлодіода
    pinMode(m_ledConfig.gpioPin, OUTPUT);

    // Початкове вимкнення світлодіода
    setLedState(false);
}

void EspModuleController::setLedState(bool turnOn) {
    m_ledState = turnOn;

    // Врахування апаратно інвертованого підключення (Active-Low)
    // Якщо activeLow == true: turnOn (true) -> LOW (0V), turnOff (false) -> HIGH (3.3V)
    uint8_t pinLevel = m_ledConfig.activeLow 
        ? (m_ledState ? LOW : HIGH) 
        : (m_ledState ? HIGH : LOW);

    digitalWrite(m_ledConfig.gpioPin, pinLevel);
}

void EspModuleController::toggleLed() {
    setLedState(!m_ledState);
}

bool EspModuleController::isLedOn() const {
    return m_ledState;
}

void EspModuleController::printDiagnosticInfo() const {
    Serial.println(F("========================================"));
    Serial.println(F("[ДІАГНОСТИКА ESP8266 МОДУЛЯ]"));
    
    if (m_revision == ModuleRevision::Esp01) {
        Serial.println(F(" Ревізія: ESP-01 (Classic)"));
        Serial.println(F(" Світлодіод: GPIO1 (TXD)"));
        Serial.println(F(" УВАГА: Оскільки LED на TXD, логування в UART може мерехтіти світлодіодом."));
        Serial.println(F(" Підтяжки: Відсутні на платі. Потрібні зовнішні резистори 10 кОм:"));
        Serial.println(F("           - CH_PD (EN) -> VCC (3.3V)"));
        Serial.println(F("           - RST        -> VCC (3.3V)"));
        Serial.println(F("           - GPIO0      -> VCC (режим RUN) / GND (режим PROG)"));
        Serial.println(F("           - GPIO2      -> VCC (3.3V)"));
    } else {
        Serial.println(F(" Ревізія: ESP-01S"));
        Serial.println(F(" Світлодіод: GPIO2"));
        Serial.println(F(" Підтяжки: Наявні внутрішні підтяжки 12 кОм на платі для:"));
        Serial.println(F("           CH_PD (EN), RST, GPIO0, GPIO2."));
        Serial.println(F("           Для прошивки достатньо підтягнути GPIO0 до GND."));
    }

    Serial.print(F(" Швидкість UART: "));
    Serial.print(m_uartConfig.baudRate);
    Serial.println(F(" бод"));

    Serial.print(F(" Поточний стан LED: "));
    Serial.println(m_ledState ? F("УВІМКНЕНО (0V / LOW)") : F("ВИМКНЕНО (3.3V / HIGH)"));
    Serial.println(F("========================================"));
}

ModuleRevision EspModuleController::getRevision() const {
    return m_revision;
}

uint8_t EspModuleController::getLedPin() const {
    return m_ledConfig.gpioPin;
}
