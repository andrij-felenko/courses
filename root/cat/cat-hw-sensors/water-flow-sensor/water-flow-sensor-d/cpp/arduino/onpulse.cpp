#include <Arduino.h>

const uint8_t SENSOR_PIN = 2;
const float K_FACTOR = 7.5;

volatile uint32_t pulse_count = 0;
uint32_t last_count = 0;
unsigned long last_time = 0;

void IRAM_ATTR onPulse() {
    pulse_count++;
}

void setup() {
    Serial.begin(115200);
    pinMode(SENSOR_PIN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(SENSOR_PIN), onPulse, FALLING);
    last_time = millis();
}

void loop() {
    unsigned long now = millis();
    if (now - last_time >= 1000) {
        uint32_t current_count;

        noInterrupts();
        current_count = pulse_count;
        interrupts();

        uint32_t pulses = current_count - last_count;
        float dt = (now - last_time) / 1000.0UL;

        float frequency = pulses / dt;
        float flow_rate = frequency / K_FACTOR;

        last_count = current_count;
        last_time = now;

        Serial.print("Частота: ");
        Serial.print(frequency, 1);
        Serial.print(" Гц | Витрата: ");
        Serial.print(flow_rate, 2);
        Serial.println(" Л/хв");
    }
}
