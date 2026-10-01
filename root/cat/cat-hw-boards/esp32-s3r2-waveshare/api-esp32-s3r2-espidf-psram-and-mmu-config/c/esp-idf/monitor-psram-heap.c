#include "esp_log.h"
#include "esp_heap_caps.h"

static const char *TAG = "HEAP_DIAG";

// Періодична діагностика стану внутрішньої та зовнішньої пам'яті
void monitor_psram_heap(void) {
    size_t free_psram = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
    size_t min_free_psram = heap_caps_get_minimum_free_size(MALLOC_CAP_SPIRAM);
    size_t largest_block = heap_caps_get_largest_free_block(MALLOC_CAP_SPIRAM);

    ESP_LOGI(TAG, "PSRAM Free: %u bytes | Min Free: %u bytes | Max Block: %u bytes",
             (unsigned int)free_psram,
             (unsigned int)min_free_psram,
             (unsigned int)largest_block);

    if (min_free_psram < 65536) {
        ESP_LOGW(TAG, "УВАГА: Критичний рівень залишку PSRAM!");
    }
}
