#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "HEAP_DEMO";

void allocate_buffers(void) {
    uint8_t *tensor_buf = (uint8_t *)heap_caps_malloc(1024 * 1024, MALLOC_CAP_SPIRAM);
    if (tensor_buf == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити пам'ять у PSRAM");
    }

    uint8_t *dma_buf = (uint8_t *)heap_caps_malloc(4096, MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL);
    if (dma_buf == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити DMA буфер в SRAM");
    }

    heap_caps_free(tensor_buf);
    heap_caps_free(dma_buf);
}
