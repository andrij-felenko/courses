// Асинхронний драйвер двофазного нагріву MQ-7 (C++ / Arduino)
#include <Arduino.h>

const uint8_t PIN_HEATER_CTRL = 9; // Вивід керування напругою (5V / 1.4V)
const uint8_t PIN_ANALOG_IN = A0;   // Аналоговий вхід сенсора

enum HeaterState {
    HEATER_HIGH_5V,
    HEATER_LOW_1V4
};

HeaterState currentPhase = HEATER_HIGH_5V;
unsigned long phaseStartTime = 0;
bool sampleTaken = false;

void initMQ7() {
    pinMode(PIN_HEATER_CTRL, OUTPUT);
    analogWrite(PIN_HEATER_CTRL, 255); // Початок циклу: 5.0 V (100% PWM)
    phaseStartTime = millis();
}

void processMQ7Cycle() {
    unsigned long currentMillis = millis();
    unsigned long elapsedTime = currentMillis - phaseStartTime;

    if (currentPhase == HEATER_HIGH_5V) {
        if (elapsedTime >= 60000UL) { // 60 секунд фази високої напруги
            currentPhase = HEATER_LOW_1V4;
            analogWrite(PIN_HEATER_CTRL, 71); // 1.4 V (приблизно 28% від 5V PWM)
            phaseStartTime = currentMillis;
            sampleTaken = false;
        }
    } else if (currentPhase == HEATER_LOW_1V4) {
        // Зчитування наприкінці вимірювальної фази (на 85-й секунді з 90)
        if (elapsedTime >= 85000UL && !sampleTaken) {
            int adcRaw = analogRead(PIN_ANALOG_IN);
            float voltage = (adcRaw / 1023.0) * 5.0;
            // Передача напруги у функцію обчислення ppm
            sampleTaken = true;
        }

        if (elapsedTime >= 90000UL) { // 90 секунд фази низької напруги
            currentPhase = HEATER_HIGH_5V;
            analogWrite(PIN_HEATER_CTRL, 255); // Перехід на 5.0 V
            phaseStartTime = currentMillis;
        }
    }
}
