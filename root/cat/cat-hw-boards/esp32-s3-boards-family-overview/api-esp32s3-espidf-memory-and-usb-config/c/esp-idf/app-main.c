#include <stdio.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "MAIN";

void app_main(void)
{
    size_t buffer_size = 512 * 1024; // 512 КБайт

    // Виділення великого буфера у зовнішній PSRAM
    uint8_t *fb_psram = (uint8_t *)heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (fb_psram == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити пам'ять у PSRAM!");
    } else {
        ESP_LOGI(TAG, "Успішно виділено %d байт у PSRAM за адресою %p", buffer_size, (void *)fb_psram);
    }

    // Виділення критичного буфера для DMA у внутрішній SRAM
    uint8_t *dma_internal = (uint8_t *)heap_caps_malloc(4096, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA);
    if (dma_internal == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити DMA-буфер у внутрішній SRAM!");
    } else {
        ESP_LOGI(TAG, "DMA-буфер виділено в SRAM за адресою %p", (void *)dma_internal);
    }

    // Звільнення пам'яті через стандартну функцію free або heap_caps_free
    heap_caps_free(fb_psram);
    heap_caps_free(dma_internal);
}
