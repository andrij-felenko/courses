#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "HEAP_EXAMPLE";

void allocate_hardware_buffers(void)
{
    /* 1. Виділення буфера для швидкого DMA-обміну по SPI (тільки внутрішня RAM!) */
    uint8_t *dma_buffer = (uint8_t *)heap_caps_malloc(4096, MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL);
    if (dma_buffer == NULL) {
        ESP_LOGE(TAG, "Помилка: не вдалося виділити DMA-буфер у внутрішній пам'яті");
        return;
    }

    /* 2. Виділення великого кадрового буфера камери у зовнішній PSRAM */
    uint8_t *frame_buffer = (uint8_t *)heap_caps_malloc(640 * 480 * 2, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (frame_buffer == NULL) {
        ESP_LOGE(TAG, "Помилка: не вдалося знайти місце у зовнішній PSRAM");
        heap_caps_free(dma_buffer);
        return;
    }

    ESP_LOGI(TAG, "Буфери успішно створено: DMA @ %p, Frame @ %p", dma_buffer, frame_buffer);

    /* Звільнення виконується універсальною функцією: алокатор сам знає, якому пулу належить адреса */
    heap_caps_free(frame_buffer);
    heap_caps_free(dma_buffer);
}
