#include <Arduino.h>
#include <avr/sleep.h>
#include <avr/power.h>

const uint8_t SOLENOID_PIN = 4;
const unsigned long PULSE_DURATION_MS = 35;

// Подання короткого імпульсу керування на соленоїд дискретного приводу
void stepEscapementPulse() {
    pinMode(SOLENOID_PIN, OUTPUT);
    
    // Подача напруги на соленоїд для відтягування собачки
    digitalWrite(SOLENOID_PIN, HIGH);
    delay(PULSE_DURATION_MS);
    
    // Зняття напруги: пружина повертає собачку для фіксації наступного зуба
    digitalWrite(SOLENOID_PIN, LOW);
}

void setup() {
    stepEscapementPulse();
    
    // Перехід мікроконтролера в режим максимально глибокого енергозбереження
    set_sleep_mode(SLEEP_MODE_PWR_DOWN);
    sleep_enable();
    sleep_mode();
}

void loop() {
    // Цикл не виконується, оскільки мікроконтролер спить
}
