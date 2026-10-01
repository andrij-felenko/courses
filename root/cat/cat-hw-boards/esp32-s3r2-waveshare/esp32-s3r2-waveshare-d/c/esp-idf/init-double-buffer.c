#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "DOUBLE_BUF";

typedef struct {
    uint16_t *buffer_a;
    uint16_t *buffer_b;
    uint16_t *active_buffer;
    size_t size;
} double_buffer_t;

bool init_double_buffer(double_buffer_t *db, size_t width, size_t height)
{
    db->size = width * height * sizeof(uint16_t);

    // Виділення двох буферів у PSRAM
    db->buffer_a = (uint16_t *)heap_caps_malloc(db->size, MALLOC_CAP_SPIRAM);
    db->buffer_b = (uint16_t *)heap_caps_malloc(db->size, MALLOC_CAP_SPIRAM);

    if (!db->buffer_a || !db->buffer_b) {
        ESP_LOGE(TAG, "Не вдалося виділити подвійний буфер у PSRAM!");
        heap_caps_free(db->buffer_a);
        heap_caps_free(db->buffer_b);
        return false;
    }

    db->active_buffer = db->buffer_a;
    ESP_LOGI(TAG, "Подвійний буфер (%zu байт кожен) успішно ініціалізовано у PSRAM", db->size);
    return true;
}

void swap_buffers(double_buffer_t *db)
{
    db->active_buffer = (db->active_buffer == db->buffer_a) ? db->buffer_b : db->buffer_a;
}
