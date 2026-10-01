#include "esp_heap_caps.h"
#include "esp_err.h"
#include "esp_log.h"

namespace {
    constexpr const char* TAG = "DIAG";
}

void print_memory_stats_cpp() {
    size_t free_sram = heap_caps_get_free_size(MALLOC_CAP_INTERNAL);
    size_t min_sram = heap_caps_get_minimum_free_size(MALLOC_CAP_INTERNAL);
    size_t free_psram = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);

    ESP_LOGI(TAG, "SRAM вільна: %zu Б, мінімум: %zu Б, PSRAM вільна: %zu Б", free_sram, min_sram, free_psram);

    if (!heap_caps_check_integrity(MALLOC_CAP_INVALID, true)) {
        ESP_LOGE(TAG, "Виявлено пошкодження кучі!");
    }
}
