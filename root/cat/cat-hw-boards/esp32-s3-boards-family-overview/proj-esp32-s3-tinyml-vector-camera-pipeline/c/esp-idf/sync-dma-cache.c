#include "esp_cache.h"
#include "esp_heap_caps.h"

// Виділення тензорної арени суворо у внутрішній швидкій SRAM
size_t arena_size = 64 * 1024; // 64 КБ
uint8_t *tensor_arena = (uint8_t *)heap_caps_malloc(arena_size, MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);

// Виділення буфера кадру у зовнішній PSRAM
size_t frame_size = 320 * 240 * 2; // 153.6 КБ
uint8_t *frame_buffer = (uint8_t *)heap_caps_malloc(frame_size, MALLOC_CAP_SPIRAM);

void sync_dma_cache(void *address, size_t size) {
    // Інвалідація кєшу для запобігання читанню застарілих даних процесором
    esp_cache_msync(address, size, ESP_CACHE_MSYNC_FLAG_DIR_M2C);
}
