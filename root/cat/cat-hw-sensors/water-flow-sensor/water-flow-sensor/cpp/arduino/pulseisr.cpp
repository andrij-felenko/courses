// Підрахунок імпульсів давача витрати води через зовнішні переривання EXTI
#include <Arduino.h>

constexpr uint8_t SENSOR_PIN = 2; // Пін з підтримкою переривань
constexpr float K_FACTOR = 7.5f;   // Імпульси за секунду на 1 Л/хв

volatile uint32_t pulseCount = 0;
uint32_t lastCalcTime = 0;

void IRAM_ATTR pulseISR() {
    pulseCount++;
}

void setup() {
    Serial.begin(115200);
    pinMode(SENSOR_PIN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(SENSOR_PIN), pulseISR, RISING);
}

void loop() {
    uint32_t currentTime = millis();
    if (currentTime - lastCalcTime >= 1000) {
        uint32_t pulses;
        
        // Атомарне копіювання змінної лічильника
        noInterrupts();
        pulses = pulseCount;
        pulseCount = 0;
        interrupts();

        float flowRate = (float)pulses / K_FACTOR;
        Serial.print("Поточна витрата: ");
        Serial.print(flowRate, 2);
        Serial.println(" Л/хв");

        lastCalcTime = currentTime;
    }
}
