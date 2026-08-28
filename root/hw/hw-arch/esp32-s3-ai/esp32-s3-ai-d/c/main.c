/* ESP-IDF / C99: Ініціалізація інференсу з розміщенням Tensor Arena у внутрішній SRAM */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "esp_heap_caps.h"
#include "esp_timer.h"
#include "esp_log.h"

#define TENSOR_ARENA_SIZE  (128 * 1024)   // 128 КБ для буферів активацій
#define ALIGNMENT_BYTES    16

static const char *TAG = "ESP32S3_AI";

// Структура дескриптора середовища інференсу
typedef struct {
    uint8_t *arena_raw;
    uint8_t *arena_aligned;
    size_t arena_size;
} inference_engine_t;

// Ініціалізація пам'яті з гарантованим вирівнюванням та розміщенням у швидкій SRAM
bool inference_engine_init(inference_engine_t *engine, size_t arena_size) {
    if (!engine || arena_size == 0) return false;

    engine->arena_size = arena_size;

    // Виділяємо пам'ять суворо у внутрішній SRAM з підтримкою DMA
    engine->arena_raw = (uint8_t *)heap_caps_malloc(
        arena_size + ALIGNMENT_BYTES,
        MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT | MALLOC_CAP_DMA
    );

    if (!engine->arena_raw) {
        ESP_LOGE(TAG, "Помилка виділення %u байтів у внутрішній SRAM!", arena_size);
        return false;
    }

    // Обчислення 16-байтного вирівняного вказівника
    uintptr_t raw_addr = (uintptr_t)engine->arena_raw;
    uintptr_t aligned_addr = (raw_addr + (ALIGNMENT_BYTES - 1)) & ~(ALIGNMENT_BYTES - 1);
    engine->arena_aligned = (uint8_t *)aligned_addr;

    ESP_LOGI(TAG, "SRAM арена успішно створена: Raw=%p, Aligned=%p (%u КБ)",
             engine->arena_raw, engine->arena_aligned, (unsigned)(arena_size / 1024));
    return true;
}

// Звільнення ресурсів
void inference_engine_deinit(inference_engine_t *engine) {
    if (engine && engine->arena_raw) {
        free(engine->arena_raw);
        engine->arena_raw = NULL;
        engine->arena_aligned = NULL;
        engine->arena_size = 0;
    }
}
