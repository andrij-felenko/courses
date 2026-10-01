#include "esp_heap_caps.h"

// Виділення буфера кадру в PSRAM з вирівнюванням по межі 64-байтової кеш-лінії L1
size_t buffer_size = 640 * 480; // Розмір кадру у байтах
size_t alignment = 64;           // Вирівнювання за розміром Octal-лінії L1 Cache

uint8_t *frame_buffer = (uint8_t *)heap_caps_aligned_alloc(
    alignment, 
    buffer_size, 
    MALLOC_CAP_SPIRAM | MALLOC_CAP_DMA
);

if (frame_buffer == NULL) {
    // Обробка помилки браку вирівняної пам'яті в PSRAM
}
