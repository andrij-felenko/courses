#include <Arduino.h>

const uint8_t RELAY_PIN = 0;

void setup() {
    // Спочатку записуємо високий рівень у вихідний регістр
    digitalWrite(RELAY_PIN, HIGH);
    // Вмикаємо режим виходу без формування низького імпульсу
    pinMode(RELAY_PIN, OUTPUT);
}

void setRelay(bool enable) {
    // Активний низький рівень перемикає реле
    digitalWrite(RELAY_PIN, enable ? LOW : HIGH);
}

void loop() {
}
