#include "esp_heap_caps.h"
#include "esp_log.h"

class FrameBufferManager {
private:
    static constexpr const char *TAG = "CAM_MEM_CPP";
    static constexpr size_t DMA_BUF_SIZE = 32 * 1024;
    static constexpr size_t PSRAM_BUF_SIZE = 512 * 1024;

    uint8_t *dma_buffer_{nullptr};
    uint8_t *psram_buffer_{nullptr};

public:
    esp_err_t initialize() {
        dma_buffer_ = static_cast<uint8_t *>(heap_caps_malloc(DMA_BUF_SIZE, MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL));
        if (!dma_buffer_) {
            ESP_LOGE(TAG, "Помилка виділення пам'яті DRAM для DMA");
            return ESP_ERR_NO_MEM;
        }

        psram_buffer_ = static_cast<uint8_t *>(heap_caps_malloc(PSRAM_BUF_SIZE, MALLOC_CAP_SPIRAM));
        if (!psram_buffer_) {
            ESP_LOGE(TAG, "Помилка виділення пам'яті PSRAM");
            heap_caps_free(dma_buffer_);
            dma_buffer_ = nullptr;
            return ESP_ERR_NO_MEM;
        }

        ESP_LOGI(TAG, "Буфери успішно ініціалізовано в пам'яті");
        return ESP_OK;
    }

    ~FrameBufferManager() {
        if (dma_buffer_) heap_caps_free(dma_buffer_);
        if (psram_buffer_) heap_caps_free(psram_buffer_);
    }
};
