#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_sleep.h"
#include "esp_log.h"

static const char *TAG = "MAIN";

void app_main(void) {
    // Встановлення періоду сну в мікросекундах (10 секунд)
    const uint64_t sleep_duration_us = 10000000;
    
    ESP_LOGI(TAG, "Підготовка до переходу в режим Deep Sleep на 10 секунд...");
    
    // Конфігурація пробудження за таймером RTC
    esp_sleep_enable_timer_wakeup(sleep_duration_us);
    
    // Затримка для завершення передачі логів через CDC USB
    vTaskDelay(pdMS_TO_TICKS(100));
    
    ESP_LOGI(TAG, "Вхід у режим сну");
    esp_deep_sleep_start();
}
