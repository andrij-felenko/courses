#include <Arduino.h>

const int KEEPALIVE_PIN = 25;
const uint64_t SLEEP_DURATION_SEC = 9;

void setup() {
    // Налаштування виводу керування баластним навантаженням
    pinMode(KEEPALIVE_PIN, OUTPUT);
    digitalWrite(KEEPALIVE_PIN, LOW);

    // Генерація короткочасного імпульсу Keep-Alive (150 мс, ~100 мА)
    digitalWrite(KEEPALIVE_PIN, HIGH);
    delay(150);
    digitalWrite(KEEPALIVE_PIN, LOW);

    // Конфігурація таймера пробудження RTC та перехід у deep-sleep
    esp_sleep_enable_timer_wakeup(SLEEP_DURATION_SEC * 1000000ULL);
    esp_deep_sleep_start();
}

void loop() {
    // У режимі deep-sleep виконання сюди не доходить
}
