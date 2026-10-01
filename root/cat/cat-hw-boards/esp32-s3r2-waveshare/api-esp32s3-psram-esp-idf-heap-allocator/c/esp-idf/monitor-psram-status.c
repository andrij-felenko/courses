#include <stdio.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "PSRAM_DIAG";

void monitor_psram_status(void) {
    size_t total_free = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
    size_t max_block = heap_caps_get_largest_free_block(MALLOC_CAP_SPIRAM);

    ESP_LOGI(TAG, "Вільна PSRAM: %zu байтів, найбільший блок: %zu байтів", total_free, max_block);

    // Перевірка цілісності купи з виведенням помилок у консоль
    if (!heap_caps_check_integrity(MALLOC_CAP_SPIRAM, true)) {
        ESP_LOGE(TAG, "Виявлено пошкодження структури купи PSRAM!");
    }
}
