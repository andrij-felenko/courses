#include <Arduino.h>

// Використання апаратного таймера для точного формування імпульсів 50 Гц
const uint8_t SERVO_PIN = 9;

void setup() {
    pinMode(SERVO_PIN, OUTPUT);
}

void setServoPulse(uint16_t pulse_us) {
    // Обмеження тривалості імпульсу безпечним діапазоном 1000–2000 мкс
    if (pulse_us < 1000) pulse_us = 1000;
    if (pulse_us > 2000) pulse_us = 2000;

    digitalWrite(SERVO_PIN, HIGH);
    delayMicroseconds(pulse_us);
    digitalWrite(SERVO_PIN, LOW);
    delayMicroseconds(20000 - pulse_us);
}

void loop() {
    // Встановлення нейтрального імпульсу 1500 мкс для калібрування зупину
    setServoPulse(1500);
}
