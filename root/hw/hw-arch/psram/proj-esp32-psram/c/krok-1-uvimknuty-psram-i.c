#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "psram";

void psram_report(void) {
    size_t total = heap_caps_get_total_size(MALLOC_CAP_SPIRAM);
    size_t free_now = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
    if (total == 0) {
        ESP_LOGE(TAG, "PSRAM не виявлено: перевір конфігурацію й чип");
        return;
    }
    ESP_LOGI(TAG, "PSRAM: усього %u КіБ, вільно %u КіБ",
             (unsigned)(total / 1024), (unsigned)(free_now / 1024));
}
