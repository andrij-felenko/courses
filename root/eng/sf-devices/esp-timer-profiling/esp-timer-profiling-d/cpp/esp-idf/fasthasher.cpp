#include <iostream>
#include <vector>
#include <cstdint>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "esp_log.h"

static const char *TAG = "TICK_LIMIT_DEMO";

class FastHasher {
public:
    static uint32_t compute(const std::vector<uint8_t>& data) {
        uint32_t hash = 5381;
        for (uint8_t b : data) {
            hash = ((hash << 5) + hash) + b;
        }
        return hash;
    }
};

extern "C" void app_main(void)
{
    std::vector<uint8_t> buffer(64, 0xAA);
    volatile uint32_t result = 0;

    TickType_t start_ticks = xTaskGetTickCount();
    for (int i = 0; i < 100; ++i) {
        result = FastHasher::compute(buffer);
    }
    TickType_t end_ticks = xTaskGetTickCount();

    int64_t start_us = esp_timer_get_time();
    for (int i = 0; i < 100; ++i) {
        result = FastHasher::compute(buffer);
    }
    int64_t end_us = esp_timer_get_time();

    ESP_LOGI(TAG, "Виміряно через FreeRTOS ticks: %u ticks (1 tick = %d ms)", 
             (unsigned int)(end_ticks - start_ticks), portTICK_PERIOD_MS);
    ESP_LOGI(TAG, "Виміряно через esp_timer: %lld us", (long long)(end_us - start_us));
}
