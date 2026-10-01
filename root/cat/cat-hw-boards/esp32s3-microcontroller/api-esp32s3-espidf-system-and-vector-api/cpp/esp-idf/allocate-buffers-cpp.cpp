#include "esp_heap_caps.h"
#include "esp_log.h"

namespace {
    constexpr const char* TAG = "HEAP_DEMO";
}

void allocate_buffers_cpp() {
    uint8_t* tensor_buf = static_cast<uint8_t*>(heap_caps_malloc(1024 * 1024, MALLOC_CAP_SPIRAM));
    if (!tensor_buf) {
        ESP_LOGE(TAG, "Не вдалося виділити пам'ять у PSRAM");
    }

    uint8_t* dma_buf = static_cast<uint8_t*>(heap_caps_malloc(4096, MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL));
    if (!dma_buf) {
        ESP_LOGE(TAG, "Не вдалося виділити DMA буфер в SRAM");
    }

    heap_caps_free(tensor_buf);
    heap_caps_free(dma_buf);
}
