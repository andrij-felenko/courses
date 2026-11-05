#include "esp_heap_caps.h"
#include "dl_model_base.hpp"

// Розмір арени під ваги, активації та вхідний тензор
#define TENSOR_ARENA_SIZE (512 * 1024)

uint8_t *allocate_tensor_arena(void) {
    // Виділення вирівняного буфера в SRAM із підтримкою DMA
    uint8_t *arena = (uint8_t *)heap_caps_aligned_alloc(
        32, 
        TENSOR_ARENA_SIZE, 
        MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA | MALLOC_CAP_8BIT
    );
    return arena;
}
