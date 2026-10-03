#include <stdio.h>
#include "esp_system.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "DRAM_MONITOR";

// Функція перевірки вільного обсягу кучі DRAM
void check_dram_health(void) {
    uint32_t free_heap = esp_get_free_heap_size();
    ESP_LOGI(TAG, "Вільна куча DRAM: %u байт", free_heap);
    
    // Перевірка критичного порогу пам'яті (менше 8 КБ)
    if (free_heap < 8192) {
        ESP_LOGW(TAG, "УВАГА: Виявлено дефіцит пам'яті DRAM! Загроза OOM.");
    }
}
