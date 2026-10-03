#include "esp_system.h"
#include "lwip/pbuf.h"
#include "esp_log.h"

static const char *TAG = "DRAM_MON";

// Перевірка безпечного рівня пам'яті перед алокацією pbuf
struct pbuf* safe_pbuf_alloc(pbuf_layer layer, uint16_t length, pbuf_type type) {
    uint32_t free_heap = esp_get_free_heap_size();
    
    // Якщо вільна куча падає нижче 4 КБ, відхиляємо нові буфери
    if (free_heap < 4096) {
        ESP_LOGE(TAG, "Критично низький рівень DRAM Heap: %u байт! Алокацію скасовано.", free_heap);
        return NULL;
    }

    struct pbuf *p = pbuf_alloc(layer, length, type);
    if (p == NULL) {
        ESP_LOGE(TAG, "Помилка pbuf_alloc: недостатньо суцільної пам'яті (фрагментація кучі)");
    } else {
        ESP_LOGI(TAG, "Успішна алокація pbuf: len=%u, залишок heap=%u", p->len, esp_get_free_heap_size());
    }
    return p;
}
