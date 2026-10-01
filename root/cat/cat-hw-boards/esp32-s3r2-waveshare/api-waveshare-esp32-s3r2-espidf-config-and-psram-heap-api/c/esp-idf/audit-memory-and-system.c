#include <stdio.h>
#include "esp_system.h"
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "SYS_AUDIT";

void audit_memory_and_system(void) {
    size_t free_psram = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
    size_t free_sram = heap_caps_get_free_size(MALLOC_CAP_INTERNAL);

    ESP_LOGI(TAG, "Вільна PSRAM: %u байт", (unsigned int)free_psram);
    ESP_LOGI(TAG, "Вільна внутрішня SRAM: %u байт", (unsigned int)free_sram);

    if (free_psram < 1024 * 1024) {
        ESP_LOGW(TAG, "Увага: доступно менше 1 МБ PSRAM!");
    }
}
