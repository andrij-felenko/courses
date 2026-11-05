#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "esp_log.h"

static const char *TAG = "TICK_LIMIT_DEMO";

// Коротка обчислювальна функція для імітації обробки даних
static void calculate_fast_hash(const uint8_t *data, size_t len, uint32_t *out_hash)
{
    uint32_t hash = 5381;
    for (size_t i = 0; i < len; ++i) {
        hash = ((hash << 5) + hash) + data[i];
    }
    *out_hash = hash;
}

void app_main(void)
{
    uint8_t buffer[64] = {0xAA};
    uint32_t result = 0;

    // Спроба вимірювання за допомогою системного тіка FreeRTOS
    TickType_t start_ticks = xTaskGetTickCount();
    for (int i = 0; i < 100; ++i) {
        calculate_fast_hash(buffer, sizeof(buffer), &result);
    }
    TickType_t end_ticks = xTaskGetTickCount();

    // Вимірювання за допомогою мікросекундного esp_timer
    int64_t start_us = esp_timer_get_time();
    for (int i = 0; i < 100; ++i) {
        calculate_fast_hash(buffer, sizeof(buffer), &result);
    }
    int64_t end_us = esp_timer_get_time();

    ESP_LOGI(TAG, "Виміряно через FreeRTOS ticks: %u ticks (1 tick = %d ms)", 
             (unsigned int)(end_ticks - start_ticks), portTICK_PERIOD_MS);
    ESP_LOGI(TAG, "Виміряно через esp_timer: %lld us", (long long)(end_us - start_us));
}
