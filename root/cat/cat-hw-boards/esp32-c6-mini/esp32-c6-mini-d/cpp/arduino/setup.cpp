#include <Arduino.h>

void setup() {
    Serial.begin(115200);
    // Очікування ініціалізації CDC USB порти
    delay(1000);

    Serial.println("Підготовка до переходу в режим Deep Sleep на 10 секунд...");

    // Встановлення періоду сну у мікросекундах (10 секунд)
    uint64_t sleep_duration_us = 10000000;
    esp_sleep_enable_timer_wakeup(sleep_duration_us);

    Serial.println("Вхід у режим сну");
    Serial.flush();

    esp_deep_sleep_start();
}

void loop() {
    // У режимі Deep Sleep після пробудження виконання починається з setup()
}
