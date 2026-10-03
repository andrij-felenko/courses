#include <stdio.h>
#include "esp_heap_caps.h"
#include "esp_lcd_panel_io.h"
#include "esp_log.h"

static const char *TAG = "LCD_CAM_DMA";

#define FRAME_WIDTH  320
#define FRAME_HEIGHT 240
#define BUFFER_SIZE  (FRAME_WIDTH * FRAME_HEIGHT * 2)

void init_dma_framebuffers(void) {
    // Виділення подвійного буфера у внутрішній SRAM з підтримкою DMA
    uint8_t *fb1 = (uint8_t *)heap_caps_aligned_alloc(64, BUFFER_SIZE, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA);
    uint8_t *fb2 = (uint8_t *)heap_caps_aligned_alloc(64, BUFFER_SIZE, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA);

    if (!fb1 || !fb2) {
        ESP_LOGE(TAG, "Критична помилка: неможливо виділити DMA буфери кадрів!");
        return;
    }

    ESP_LOGI(TAG, "DMA буфери кадрів успішно створено. FB1: %p, FB2: %p", fb1, fb2);

    // Звільнення ресурсів після використання
    heap_caps_free(fb1);
    heap_caps_free(fb2);
}
