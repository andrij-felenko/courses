#include <stdio.h>
#include <stddef.h>
#include <stdint.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "buffer_alloc";

// Функція для створення вирівняного кадрового буфера у PSRAM
uint8_t* allocate_frame_buffer(size_t width, size_t height, size_t bytes_per_pixel) {
    size_t total_size = width * height * bytes_per_pixel;
    
    // Вирівнювання розміру та пам'яті по межі 64-байтної кеш-лінії
    size_t alignment = 64;
    
    // Виділення вирівняної пам'яті у зовнішній PSRAM з можливістю DMA
    uint8_t *buffer = (uint8_t *)heap_caps_aligned_alloc(alignment, total_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    
    if (buffer == NULL) {
        ESP_LOGE(TAG, "Помилка виділення буфера у PSRAM обсягом %zu байтів", total_size);
        return NULL;
    }
    
    ESP_LOGI(TAG, "Буфер у PSRAM успішно виділено за адресою %p", (void*)buffer);
    return buffer;
}
