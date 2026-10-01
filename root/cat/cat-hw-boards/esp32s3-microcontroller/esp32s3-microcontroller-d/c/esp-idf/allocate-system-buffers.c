#include "esp_heap_caps.h"
#include <stdio.h>

// Приклад безпечного розподілу пам'яті за категоріями у середовищі ESP-IDF
void allocate_system_buffers(void) {
    // 1. Алокація великого масиву у зовнішній PSRAM (2 МБ)
    size_t psram_size = 2 * 1024 * 1024;
    uint8_t *model_weights = (uint8_t *)heap_caps_malloc(psram_size, MALLOC_CAP_SPIRAM);

    // 2. Алокація критичного буфера у внутрішній SRAM
    size_t isr_buf_size = 1024;
    uint8_t *isr_buffer = (uint8_t *)heap_caps_malloc(isr_buf_size, MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);

    // 3. Алокація буфера з підтримкою апаратного DMA
    size_t dma_buf_size = 4096;
    uint8_t *dma_buffer = (uint8_t *)heap_caps_malloc(dma_buf_size, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA);

    if (!model_weights || !isr_buffer || !dma_buffer) {
        // Обробка відмови розподілу пам'яті
        heap_caps_free(model_weights);
        heap_caps_free(isr_buffer);
        heap_caps_free(dma_buffer);
    }
}
