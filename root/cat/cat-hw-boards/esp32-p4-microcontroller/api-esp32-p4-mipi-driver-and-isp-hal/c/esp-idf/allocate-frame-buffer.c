#include <stdio.h>
#include <stddef.h>
#include <stdint.h>
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_cache.h"

static const char *TAG = "video_buffer";

#ifndef SOC_CACHE_LINE_SIZE
#define SOC_CACHE_LINE_SIZE 64
#endif

// Функція виділення кадрового буфера в PSRAM з вирівнюванням під DMA та кеш-лінії
uint8_t* allocate_frame_buffer(size_t width, size_t height, size_t bytes_per_pixel) {
    size_t raw_size = width * height * bytes_per_pixel;
    // Обчислення вирівняного розміру кратно 64 байтам
    size_t aligned_size = (raw_size + SOC_CACHE_LINE_SIZE - 1) & ~(SOC_CACHE_LINE_SIZE - 1);

    // Виділення пам'яті в PSRAM із вирівнюванням адреси по межі кеш-лінії
    uint8_t *fb = (uint8_t *)heap_caps_aligned_alloc(
        SOC_CACHE_LINE_SIZE,
        aligned_size,
        MALLOC_CAP_SPIRAM | MALLOC_CAP_DMA
    );

    if (fb == NULL) {
        ESP_LOGE(TAG, "Помилка: не вдалося виділити %zu байтів у PSRAM для DMA", aligned_size);
        return NULL;
    }

    ESP_LOGI(TAG, "Успішно виділено DMA-буфер: %p, вирівняний розмір: %zu байтів", fb, aligned_size);
    return fb;
}
