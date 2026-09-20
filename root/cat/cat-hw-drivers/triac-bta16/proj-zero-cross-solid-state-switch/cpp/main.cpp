#include <Arduino.h>
#include "TriacDriver.h"

// Призначення GPIO пина для керування симістором BTA16-600B через оптопару (наприклад, MOC3041)
constexpr uint8_t TRIAC_PIN = 5;

// Створення екземпляра драйвера (активний рівень HIGH)
TriacDriver triac(TRIAC_PIN, true);

// Змінні для демонстрації періодичної роботи у main/loop
unsigned long lastActionTime = 0;
constexpr unsigned long ACTION_INTERVAL = 10000; // 10 секунд

void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 2000) {
        // Очікування ініціалізації послідовного порту (для плати з USB)
    }

    Serial.println(F("Ініціалізація системи керування симісторним ключем BTA16-600B..."));

    // Безпечна ініціалізація драйвера
    triac.begin();

    Serial.println(F("Драйвер успішно ініціалізовано у безпечному (вимкненому) стані."));

    // Демонстрація: вмикаємо симістор на 3 секунди за допомогою неблокуючого таймера
    Serial.println(F("Увімкнення навантаження на 3000 мс (неблокуюче автовимкнення)..."));
    triac.turnOnFor(3000);
    lastActionTime = millis();
}

void loop() {
    // 1. Обов'язкове оновлення стану драйвера в кожному циклі loop()
    triac.update();

    // 2. Демонстрація виконання інших завдань без затримок (delay)
    static unsigned long lastLogTime = 0;
    if (millis() - lastLogTime >= 500) {
        lastLogTime = millis();
        
        if (triac.isTimerActive()) {
            Serial.print(F("Стан симістора: УВІМКНЕНО | Залишок часу: "));
            Serial.print(triac.getRemainingTimeMs());
            Serial.println(F(" мс"));
        }
    }

    // 3. Періодичний запуск симістора для демонстрації роботи
    if (millis() - lastActionTime >= ACTION_INTERVAL) {
        lastActionTime = millis();
        Serial.println(F("[Подія] Циклічний запуск: Увімкнення симістора на 4000 мс..."));
        triac.turnOnFor(4000);
    }
}
