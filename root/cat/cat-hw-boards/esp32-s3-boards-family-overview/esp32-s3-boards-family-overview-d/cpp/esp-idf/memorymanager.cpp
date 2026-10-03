#include <iostream>
#include <memory>
#include "esp_heap_caps.h"
#include "esp_log.h"

class MemoryManager {
public:
    MemoryManager(size_t spiram_bytes, size_t dma_bytes) {
        // Виділення вирівняного блоку в PSRAM для обчислень
        m_spiram_ptr = static_cast<uint8_t*>(heap_caps_malloc(spiram_bytes, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
        
        // Виділення буфера у внутрішній SRAM для периферійного DMA
        m_dma_ptr = static_cast<uint8_t*>(heap_caps_malloc(dma_bytes, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA));

        if (!m_spiram_ptr || !m_dma_ptr) {
            ESP_LOGE("MemoryManager", "Не вдалося виділити необхідні сегменти пам'яті");
        }
    }

    ~MemoryManager() {
        if (m_spiram_ptr) heap_caps_free(m_spiram_ptr);
        if (m_dma_ptr) heap_caps_free(m_dma_ptr);
    }

    uint8_t* get_spiram_buffer() const { return m_spiram_ptr; }
    uint8_t* get_dma_buffer() const { return m_dma_ptr; }

private:
    uint8_t* m_spiram_ptr{nullptr};
    uint8_t* m_dma_ptr{nullptr};
};

extern "C" void app_main(void)
{
    MemoryManager mem(1024 * 512, 2048);
    if (mem.get_spiram_buffer() && mem.get_dma_buffer()) {
        ESP_LOGI("CPP_MAIN", "Пам'ять успішно виділено через RAII-обгортку");
    }
}
