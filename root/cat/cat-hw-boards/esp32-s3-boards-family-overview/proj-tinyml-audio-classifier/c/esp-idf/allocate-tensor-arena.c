#include <stddef.h>
#include <stdint.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "TFLITE_MEM";

// Виділення 16-байтово вирівняної тензорної арени у внутрішній SRAM
uint8_t* allocate_tensor_arena(size_t arena_size) {
    // 16-байтове вирівнювання обов'язкове для векторних інструкцій Xtensa PIE
    uint8_t *arena = (uint8_t *)heap_caps_aligned_alloc(
        16, 
        arena_size, 
        MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT
    );
    
    if (arena == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити %zu байт у внутрішній SRAM!", arena_size);
        return NULL;
    }
    
    ESP_LOGI(TAG, "Тензорну арену (%zu байт) успішно розміщено у SRAM", arena_size);
    return arena;
}
