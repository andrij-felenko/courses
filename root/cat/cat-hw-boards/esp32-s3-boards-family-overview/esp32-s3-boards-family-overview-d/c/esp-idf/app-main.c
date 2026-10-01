#include "esp_system.h"
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "MAIN";

void app_main(void) {
    // Перевірка наявності та розміру зовнішньої пам'яті PSRAM
    size_t psram_size = heap_caps_get_total_size(MALLOC_CAP_SPIRAM);
    ESP_LOGI(TAG, "Загальний обсяг PSRAM: %d байт", psram_size);

    // Виділення динамічного буфера кадру в зовнішній пам'яті
    uint8_t *frame_buffer = (uint8_t *)heap_caps_malloc(640 * 480, MALLOC_CAP_SPIRAM);
    if (frame_buffer == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити пам'ять у PSRAM!");
    } else {
        ESP_LOGI(TAG, "Буфер кадру успішно виділено в PSRAM");
        heap_caps_free(frame_buffer);
    }
}
