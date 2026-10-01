#include <stdio.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "PSRAM_DEMO";

void app_main(void)
{
    // Виділення буфера 100 КБ у зовнішній PSRAM
    uint8_t *psram_buffer = (uint8_t *)heap_caps_malloc(100 * 1024, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    
    if (psram_buffer == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити пам'ять у PSRAM!");
        return;
    }

    ESP_LOGI(TAG, "Буфер у PSRAM успішно виділено за адресою: %p", psram_buffer);
    
    // Звільнення пам'яті
    heap_caps_free(psram_buffer);
}
