#include "esp_heap_caps.h"
#include "esp_log.h"

class PsramManager {
public:
    static uint8_t* allocate_dma_aligned(size_t size) {
        // Виділення пам'яті з прапорцями під DMA та вирівнюванням
        void* ptr = heap_caps_aligned_alloc(16, size, MALLOC_CAP_SPIRAM | MALLOC_CAP_DMA);
        if (!ptr) {
            ESP_LOGE("PSRAM", "Помилка виділення DMA буфера у PSRAM");
            return nullptr;
        }
        return static_cast<uint8_t*>(ptr);
    }
};
