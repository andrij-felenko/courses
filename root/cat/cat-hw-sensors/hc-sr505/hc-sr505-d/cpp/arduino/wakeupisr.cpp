#include <Arduino.h>
#include <avr/sleep.h>
#include <avr/interrupt.h>

const uint8_t PIR_PIN = 2; // Вхід з підтримкою зовнішнього переривання INT0
volatile bool motionDetected = false;

void wakeUpISR() {
    motionDetected = true;
}

void setup() {
    pinMode(PIR_PIN, INPUT_PULLDOWN);
    attachInterrupt(digitalPinToInterrupt(PIR_PIN), wakeUpISR, RISING);
}

void loop() {
    if (motionDetected) {
        motionDetected = false;
        // Виконання дій після пробудження системи
        delay(100); 
    }
    
    // Перехід у режим глибокого збереження енергії
    set_sleep_mode(SLEEP_MODE_PWR_DOWN);
    sleep_enable();
    sleep_cpu();
    
    // Продовження роботи після виходу з переривання
    sleep_disable();
}
