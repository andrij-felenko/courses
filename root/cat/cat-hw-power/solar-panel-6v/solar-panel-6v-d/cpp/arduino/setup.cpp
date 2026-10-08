#include <Arduino.h>

const int SOLAR_ADC_PIN = 34;
const int POWER_GATE_PIN = 25;

const float VOLTAGE_DIVIDER_RATIO = 2.0f; // Знущальний дільник напруги (100к / 100к)
const uint32_t SOLAR_V_MIN_MV = 4600;     // Поріг зниження напруги панелі
const uint32_t SOLAR_V_HYST_MV = 4900;    // Поріг відновлення роботи

bool is_load_active = false;

void setup() {
    pinMode(POWER_GATE_PIN, OUTPUT);
    digitalWrite(POWER_GATE_PIN, LOW);
    analogReadResolution(12);
}

void loop() {
    uint32_t raw_adc = analogRead(SOLAR_ADC_PIN);
    uint32_t solar_mv = (uint32_t)((raw_adc * 3300.0f / 4095.0f) * VOLTAGE_DIVIDER_RATIO);

    if (is_load_active && (solar_mv < SOLAR_V_MIN_MV)) {
        is_load_active = false;
        digitalWrite(POWER_GATE_PIN, LOW); // Відключаємо споживання при виснаженні інсоляції
    } else if (!is_load_active && (solar_mv > SOLAR_V_HYST_MV)) {
        is_load_active = true;
        digitalWrite(POWER_GATE_PIN, HIGH); // Відновлюємо споживання при накопиченні напруги
    }
    delay(100);
}
