#include <Arduino.h>

RTC_DATA_ATTR uint32_t bootCount = 0;

void setup() {
    Serial.begin(115200);
    bootCount++;
    Serial.printf("[POWER] Лічильник перезавантажень в RTC RAM: %u\n", bootCount);

    // Встановлення таймера Deep-Sleep на 60 секунд
    esp_sleep_enable_timer_wakeup(60 * 1000000ULL);
    Serial.println("[POWER] Перехід у режим глибокого сну");
    Serial.flush();

    esp_deep_sleep_start();
}

void loop() {
    // Порожній цикл, оскільки контролер засинає в setup()
}
