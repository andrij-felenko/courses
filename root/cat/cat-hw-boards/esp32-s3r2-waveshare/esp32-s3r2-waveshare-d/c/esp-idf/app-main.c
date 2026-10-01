#include <stdio.h>
#include "esp_system.h"
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "main";

void app_main(void)
{
    size_t frame_size = 640 * 480 * 2; // 614.4 КБ для кадру RGB565
    uint8_t *frame_buffer = (uint8_t *)heap_caps_malloc(frame_size, MALLOC_CAP_SPIRAM);

    if (frame_buffer == NULL) {
        ESP_LOGE(TAG, "Помилка виділення пам'яті в PSRAM!");
        return;
    }

    ESP_LOGI(TAG, "Буфер у PSRAM успішно виділено за адресою: %p", frame_buffer);
    ESP_LOGI(TAG, "Вільна PSRAM: %d байт", heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
    ESP_LOGI(TAG, "Вільна внутрішня SRAM: %d байт", heap_caps_get_free_size(MALLOC_CAP_INTERNAL));

    heap_caps_free(frame_buffer);
}
