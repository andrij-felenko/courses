// Приклад скидання WDT у середовищі C++ (ESP8266 Arduino Core)
#include <Arduino.h>

void executeHeavyComputation() {
    Serial.println("Запуск обчислювального циклу...");

    for (uint32_t i = 0; i < 20000; i++) {
        delayMicroseconds(150);

        // Педіодичний виклик скидання WDT у C++
        if (i % 5000 == 0) {
            ESP.wdtFeed(); // Аліас до system_soft_wdt_feed()
            Serial.printf("WDT Feed, крок %u\n", i);
        }
    }

    Serial.println("Цикл завершено успішно!");
}
