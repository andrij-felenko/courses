#include <Arduino.h>

const int KEEP_ALIVE_PIN = 18;
unsigned long lastPulseTime = 0;
const unsigned long PULSE_INTERVAL_MS = 15000;

void setup() {
    pinMode(KEEP_ALIVE_PIN, OUTPUT);
    digitalWrite(KEEP_ALIVE_PIN, LOW);
}

void loop() {
    unsigned long currentMillis = millis();
    
    // Скидання 30-секундного таймера сну IP5310 кожні 15 секунд
    if (currentMillis - lastPulseTime >= PULSE_INTERVAL_MS) {
        lastPulseTime = currentMillis;
        
        digitalWrite(KEEP_ALIVE_PIN, HIGH);
        delay(150);
        digitalWrite(KEEP_ALIVE_PIN, LOW);
    }
    
    // Основна робота мікроконтролера у режимі низького споживання
}
