#include "esp_sleep.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_LED GPIO_NUM_2

void app_main(void) {
    // 1. корисна робота (тут — блимнути, а реально: виміряти й записати)
    gpio_set_direction(PIN_LED, GPIO_MODE_OUTPUT);
    gpio_set_level(PIN_LED, 1);
    vTaskDelay(pdMS_TO_TICKS(20));
    gpio_set_level(PIN_LED, 0);

    // 2. звести RTC-будильник на 8 с і заснути найглибше
    ESP_ERROR_CHECK(esp_sleep_enable_timer_wakeup(8ULL * 1000000));  // мікросекунди
    esp_deep_sleep_start();
    // ← сюди керування НЕ повертається: після глибокого сну чип стартує наново,
    //   з початку app_main. Стан, який має пережити сон, кладуть у RTC-пам'ять.
}
