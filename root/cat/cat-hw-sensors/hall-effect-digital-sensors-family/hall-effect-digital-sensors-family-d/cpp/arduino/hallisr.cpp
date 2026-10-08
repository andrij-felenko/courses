// C++ (Arduino) — Обробка переривання цифрового давача Холла
#include <Arduino.h>

const uint8_t HALL_PIN = 2;
volatile uint32_t pulseCount = 0;

void IRAM_ATTR hallIsr() {
    pulseCount++;
}

void setup() {
    Serial.begin(115200);
    // Вхід із внутрішнім підтягувальним резистором
    pinMode(HALL_PIN, INPUT_PULLUP);
    // Реєстрація переривання по спадаючому фронту (активний LOW)
    attachInterrupt(digitalPinToInterrupt(HALL_PIN), hallIsr, FALLING);
}

void loop() {
    static uint32_t lastPrint = 0;
    if (millis() - lastPrint >= 1000) {
        lastPrint = millis();
        noInterrupts();
        uint32_t count = pulseCount;
        interrupts();
        Serial.print(F("Оберти за секунду: "));
        Serial.println(count);
    }
}
