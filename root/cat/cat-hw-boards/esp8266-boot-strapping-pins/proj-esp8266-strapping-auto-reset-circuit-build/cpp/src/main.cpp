#include <Arduino.h>
#include "EspBootMonitor.hpp"

// Екземпляр класу для моніторингу завантаження ESP8266
static EspBootMonitor bootMonitor;

// Період неблокуючого виводу статусу в послідовний порт (5 секунд)
static constexpr uint32_t REPORT_INTERVAL_MS = 5000;
static uint32_t lastReportTime = 0;

void setup() {
    // Ініціалізація послідовного порту UART на швидкості 115200 бод
    Serial.begin(115200);

    // Короткі затримка для стабілізації напрямку ліній UART після скидання
    delay(500);

    Serial.println();
    Serial.println(F("[SYSTEM] Ініціалізація модулю моніторингу завантаження ESP8266..."));

    // Ініціалізація монітора: підтяжка виводів та збереження початкового стану старту
    bootMonitor.begin();

    // Вивід початкового діагностичного звіту завантаження
    Serial.println(F("[SYSTEM] Початковий стан завантаження мікроконтролера:"));
    BootStatusReport initialReport = bootMonitor.getInitialBootReport();
    Serial.print(initialReport.toString());

    lastReportTime = millis();
}

void loop() {
    uint32_t currentTime = millis();

    // Неблокуючий періодичний вивід статусу (без використання delay, що запобігає WDT reset)
    if (currentTime - lastReportTime >= REPORT_INTERVAL_MS) {
        lastReportTime = currentTime;

        Serial.println(F("[MONITOR] Періодична перевірка поточного стану виводів:"));
        BootStatusReport currentReport = bootMonitor.sampleCurrentState();

        Serial.print(F("Поточний стан: GPIO0="));
        Serial.print(currentReport.gpio0State ? "1" : "0");
        Serial.print(F(", GPIO2="));
        Serial.print(currentReport.gpio2State ? "1" : "0");
        Serial.print(F(", GPIO15="));
        Serial.print(currentReport.gpio15State ? "1" : "0");
        Serial.print(F(" -> Режим: "));
        Serial.println(EspBootMonitor::bootModeToString(currentReport.mode));
        Serial.println(F("-----------------------------------------------------"));
    }

    // Інші неблокуючі завдання...
    yield(); // Годування системного watchdog таймера ESP8266
}
