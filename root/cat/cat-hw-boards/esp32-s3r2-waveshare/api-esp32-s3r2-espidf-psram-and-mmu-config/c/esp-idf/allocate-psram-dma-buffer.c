#include <stddef.h>
#include <stdint.h>
#include "esp_heap_caps.h"
#include "esp_cache.h"
#include "esp_log.h"

static const char *TAG = "psram_dma";

// Атомарне виділення вирівняного буфера в PSRAM та синхронізація кешу
uint8_t* allocate_psram_dma_buffer(size_t size, size_t alignment) {
    // Виділення вирівняного буфера по межі кеш-лінії
    uint8_t *buffer = (uint8_t *)heap_caps_aligned_alloc(alignment, size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (buffer == NULL) {
        ESP_LOGE(TAG, "Помилка виділення пам'яті в PSRAM");
        return NULL;
    }

    // Заповнення буфера даними
    for (size_t i = 0; i < size; i++) {
        buffer[i] = (uint8_t)(i & 0xFF);
    }

    // Примусове скидання даних з кешу L1 у PSRAM перед передачею
    esp_err_t err = esp_cache_msync(buffer, size, ESP_CACHE_MSYNC_FLAG_DIR_C2M | ESP_CACHE_MSYNC_FLAG_INVALIDATE);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка синхронізації кешу: %d", err);
    }

    return buffer;
}
