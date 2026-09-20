#include <Arduino.h>
#include "PhaseSelector.h"

// Аналогові піни вимірювання напруги через трансформаторні або опторозв'язані датчики
constexpr uint8_t PIN_VOLT_L1 = A0;
constexpr uint8_t PIN_VOLT_L2 = A1;
constexpr uint8_t PIN_VOLT_L3 = A2;

// Цифрові піни керування реле фаз L1, L2, L3
constexpr uint8_t PIN_RELAY_L1 = 8;
constexpr uint8_t PIN_RELAY_L2 = 9;
constexpr uint8_t PIN_RELAY_L3 = 10;

// Конфігурація контролера перемикача фаз
const PhaseConfig config = {
    .pinVoltL1 = PIN_VOLT_L1,
    .pinVoltL2 = PIN_VOLT_L2,
    .pinVoltL3 = PIN_VOLT_L3,

    .pinRelayL1 = PIN_RELAY_L1,
    .pinRelayL2 = PIN_RELAY_L2,
    .pinRelayL3 = PIN_RELAY_L3,

    .voltageScaleFactor = 0.4884f, // 1023 -> 500V RMS
    .uMin = 180.0f,                // Нижній поріг (В)
    .uMax = 250.0f,                // Верхній поріг (В)
    .uHysteresis = 5.0f,           // Гістерезис повернення у норму (В)

    .deadTimeMs = 500,             // Пауза між перемиканнями контакторів (мс)
    .returnDelayMs = 5000          // Затримка повернення на L1 (мс)
};

// Об'єкт контролера
PhaseSelector selector(config);

uint32_t lastReportTime = 0;

void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 3000) {}

    selector.begin();
    Serial.println(F("Контролер автоматичного перемикача фаз запущено."));
}

void loop() {
    // Оновлення стану контролера в кожному циклі без затримок delay()
    selector.update();

    // Періодичний телеметричний звіт кожну секунду
    uint32_t now = millis();
    if (now - lastReportTime >= 1000) {
        lastReportTime = now;

        Serial.print(F("U_L1: ")); Serial.print(selector.getVoltage(PhaseId::L1), 1); Serial.print(F("V | "));
        Serial.print(F("U_L2: ")); Serial.print(selector.getVoltage(PhaseId::L2), 1); Serial.print(F("V | "));
        Serial.print(F("U_L3: ")); Serial.print(selector.getVoltage(PhaseId::L3), 1); Serial.println(F("V"));

        Serial.print(F("Активна фаза: "));
        switch (selector.getActivePhase()) {
            case PhaseId::L1: Serial.println(F("L1 (Пріоритетна)")); break;
            case PhaseId::L2: Serial.println(F("L2 (Резерв 1)")); break;
            case PhaseId::L3: Serial.println(F("L3 (Резерв 2)")); break;
            case PhaseId::NONE: Serial.println(F("ВІДСУТНЯ (Аварія мережі)")); break;
        }
    }
}
