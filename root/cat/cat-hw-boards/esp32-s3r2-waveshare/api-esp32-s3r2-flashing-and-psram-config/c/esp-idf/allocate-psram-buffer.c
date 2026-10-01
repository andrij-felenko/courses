#include <stdio.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

void allocate_psram_buffer(void) {
    size_t free_psram = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
    ESP_LOGI("PSRAM", "Вільна PSRAM: %u байт", free_psram);

    size_t buffer_size = 1024 * 1024; // 1 МБ
    uint8_t *buffer = (uint8_t *)heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM);

    if (buffer == NULL) {
        ESP_LOGE("PSRAM", "Помилка виділення буфера у PSRAM!");
        return;
    }

    ESP_LOGI("PSRAM", "Виділено 1 МБ за адресою: %p", buffer);
    heap_caps_free(buffer);
}
