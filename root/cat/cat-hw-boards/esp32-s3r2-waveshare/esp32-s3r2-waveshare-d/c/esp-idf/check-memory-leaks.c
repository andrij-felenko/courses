#include "esp_log.h"
#include "esp_heap_caps.h"
#include "esp_system.h"

static const char *TAG = "USB_DEBUG";

void check_memory_leaks(void) {
    // Перевірка цілісності купи та виведення вільного обсягу PSRAM і SRAM
    size_t free_sram = heap_caps_get_free_size(MALLOC_CAP_INTERNAL);
    size_t free_psram = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
    ESP_LOGI(TAG, "Вільна SRAM: %u байт, вільна PSRAM: %u байт", free_sram, free_psram);

    if (!heap_caps_check_integrity_all(true)) {
        ESP_LOGE(TAG, "Виявлено пошкодження купи пам'яті!");
    }
}
