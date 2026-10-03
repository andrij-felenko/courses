#include <cstdint>
#include <cstddef>
#include "esp_heap_caps.h"
#include "esp_log.h"

class FramebufferManager {
private:
    static constexpr const char *TAG = "LCD_CAM_DMA";
    static constexpr size_t WIDTH = 320;
    static constexpr size_t HEIGHT = 240;
    static constexpr size_t BUF_SIZE = WIDTH * HEIGHT * 2;

public:
    static void setupBuffers() {
        uint8_t *fb1 = static_cast<uint8_t*>(heap_caps_aligned_alloc(64, BUF_SIZE, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA));
        uint8_t *fb2 = static_cast<uint8_t*>(heap_caps_aligned_alloc(64, BUF_SIZE, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA));

        if (!fb1 || !fb2) {
            ESP_LOGE(TAG, "Не вдалося виділити подвійні DMA буфери");
            return;
        }

        ESP_LOGI(TAG, "Успішно створено DMA буфери. FB1: %p, FB2: %p", fb1, fb2);

        heap_caps_free(fb1);
        heap_caps_free(fb2);
    }
};
