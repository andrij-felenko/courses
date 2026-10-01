#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "psram_mem";

uint8_t* allocate_psram_buffer(size_t size) {
    // Виділення буфера у зовнішній PSRAM з можливістю 8-бітної адресації
    uint8_t *buffer = (uint8_t *)heap_caps_malloc(size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (!buffer) {
        ESP_LOGE(TAG, "Не вдалося виділити %zu байтів у PSRAM", size);
        return NULL;
    }
    ESP_LOGI(TAG, "Успішно виділено %zu байтів у PSRAM за адресою %p", size, (void*)buffer);
    return buffer;
}
