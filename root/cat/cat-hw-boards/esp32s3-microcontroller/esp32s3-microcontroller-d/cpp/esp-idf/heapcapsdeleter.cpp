#include "esp_heap_caps.h"
#include <cstdint>
#include <cstddef>
#include <memory>

// Приклад C++ обгортки з RAII для керування категоріями пам'яті ESP-IDF
struct HeapCapsDeleter {
    void operator()(void *ptr) const {
        heap_caps_free(ptr);
    }
};

template <typename T>
using SystemBufferPtr = std::unique_ptr<T[], HeapCapsDeleter>;

void allocate_system_buffers_cpp(void) {
    // Алокація масиву ваг у зовнішній пам'яті PSRAM
    const size_t psram_size = 2 * 1024 * 1024;
    SystemBufferPtr<uint8_t> model_weights(static_cast<uint8_t *>(heap_caps_malloc(psram_size, MALLOC_CAP_SPIRAM)));

    // Алокація DMA-буфера у внутрішній SRAM
    const size_t dma_buf_size = 4096;
    SystemBufferPtr<uint8_t> dma_buffer(static_cast<uint8_t *>(heap_caps_malloc(dma_buf_size, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA)));

    if (!model_weights || !dma_buffer) {
        // Обробка помилки розподілу
    }
}
