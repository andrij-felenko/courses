#include <stdio.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "HEAP_MONITOR";

void check_memory_status(void) {
    size_t free_psram = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
    size_t largest_psram_block = heap_caps_get_largest_free_block(MALLOC_CAP_SPIRAM);
    size_t free_sram = heap_caps_get_free_size(MALLOC_CAP_INTERNAL);

    ESP_LOGI(TAG, "Стан кучі: Вільна PSRAM = %zu Б, Найбільший блок PSRAM = %zu Б, Вільна SRAM = %zu Б",
             free_psram, largest_psram_block, free_sram);
}

uint8_t* safe_psram_alloc(size_t required_bytes) {
    size_t largest_block = heap_caps_get_largest_free_block(MALLOC_CAP_SPIRAM);
    if (largest_block < required_bytes) {
        ESP_LOGW(TAG, "Неможливо виділити %zu Б: найбільший блок у PSRAM лише %zu Б",
                 required_bytes, largest_block);
        return NULL;
    }
    return (uint8_t *)heap_caps_malloc(required_bytes, MALLOC_CAP_SPIRAM);
}
