#include <Arduino.h>

// Змінна зберігається в RTC пам'яті між циклами глибокого сну
RTC_DATA_ATTR int bootCount = 0;

void setup() {
    Serial.begin(115200);
    delay(1000);

    bootCount++;
    Serial.printf("Номер запуску пристрою: %d\n", bootCount);

    // Встановлення таймера пробудження на 10 секунд
    esp_sleep_enable_timer_wakeup(10 * 1000000ULL);

    Serial.println("Вхід у режим Deep Sleep...");
    Serial.flush();
    
    esp_deep_sleep_start();
}

void loop() {
    // Цей код ніколи не виконується, оскільки пробудження перезапускає setup()
}
