#include "SafetyRopeSwitch.h"

// Призначення пінів для Arduino Uno / Nano / ESP32
const uint8_t PIN_ROPE_NC1 = 2;       // Канал 1 тросового вимикача
const uint8_t PIN_ROPE_NC2 = 3;       // Канал 2 тросового вимикача
const uint8_t PIN_RESET_BTN = 4;      // Кнопка свідомого скиду Reset
const uint8_t PIN_SAFETY_RELAY = 8;   // Силове реле дозволу роботи приводу
const uint8_t PIN_ALARM_LED = 13;     // Світлодіод індикації аварійного стану

// Конфігурація обробника тросового вимикача
SafetyRopeSwitchConfig switchConfig = {
    PIN_ROPE_NC1,       // ch1Pin
    PIN_ROPE_NC2,       // ch2Pin
    PIN_RESET_BTN,      // resetPin
    10,                 // debounceMs = 10 мс
    50                  // discrepancyTimeoutMs = 50 мс
};

SafetyRopeSwitch ropeSwitch(switchConfig);

SafetyState lastReportedState = SafetyState::SYSTEM_OK;
uint32_t lastPrintMs = 0;

void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 2000) {} // Затримка для стабілізації Serial

    Serial.println(F("=== СИСТЕМА КОНТРОЛЮ ТРОСОВОГО ВИМИКАЧА (IEC 60947-5-5) ==="));

    // Налаштування виходів керування
    pinMode(PIN_SAFETY_RELAY, OUTPUT);
    pinMode(PIN_ALARM_LED, OUTPUT);

    // Первинний вимкнений стан для безпеки
    digitalWrite(PIN_SAFETY_RELAY, LOW);
    digitalWrite(PIN_ALARM_LED, HIGH);

    ropeSwitch.begin();
    lastReportedState = ropeSwitch.getState();
    Serial.print(F("Початковий стан: "));
    Serial.println(ropeSwitch.getStateName());
}

void loop() {
    // Оновлення стану неблокуючого кінцевого автомата
    ropeSwitch.update();

    SafetyState currentState = ropeSwitch.getState();

    // Реагування на зміну стану безпеки
    if (currentState != lastReportedState) {
        lastReportedState = currentState;

        Serial.print(F("[ЗМІНА СТАНУ] Новий статус: "));
        Serial.println(ropeSwitch.getStateName());

        if (ropeSwitch.isSystemOk()) {
            // Вмикаємо реле приводу, вимикаємо тривогу
            digitalWrite(PIN_SAFETY_RELAY, HIGH);
            digitalWrite(PIN_ALARM_LED, LOW);
            Serial.println(F("-> Реле живлення УВІМКНЕНО. Обладнання готова до роботи."));
        } else {
            // Розмикаємо коло безпеки приводу
            digitalWrite(PIN_SAFETY_RELAY, LOW);
            digitalWrite(PIN_ALARM_LED, HIGH);
            Serial.println(F("-> Реле живлення ВИМКНЕНО! Аварійне блокування приводу."));
        }
    }

    // Періодичне виведення стану раз на 2 секунди
    if (millis() - lastPrintMs >= 2000) {
        lastPrintMs = millis();
        Serial.print(F("Поточний стан лінії: "));
        Serial.println(ropeSwitch.getStateName());
    }
}
