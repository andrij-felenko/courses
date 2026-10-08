// Керування силовим контактором у C++ (Arduino Framework)
#include <Arduino.h>

const int CONTACTOR_PIN = 5;
const unsigned long MIN_PAUSE_MS = 1000;
unsigned long lastSwitchTime = 0;

void setupContactor() {
    pinMode(CONTACTOR_PIN, OUTPUT);
    digitalWrite(CONTACTOR_PIN, LOW);
}

bool setContactor(bool enable) {
    unsigned long now = millis();
    if (now - lastSwitchTime < MIN_PAUSE_MS) {
        Serial.println("Увага: захисне блокування за часом!");
        return false;
    }
    digitalWrite(CONTACTOR_PIN, enable ? HIGH : LOW);
    lastSwitchTime = now;
    Serial.print("Контактор стан: ");
    Serial.println(enable ? "ON" : "OFF");
    return true;
}
