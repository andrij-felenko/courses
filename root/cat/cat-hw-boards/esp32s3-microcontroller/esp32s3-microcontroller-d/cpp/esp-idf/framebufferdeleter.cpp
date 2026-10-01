#include "esp_heap_caps.h"
#include <cstdint>
#include <cstddef>
#include <memory>

// Обгортка кадрового буфера в C++ із автоматичним звільненням пам'яті
struct FrameBufferDeleter {
    void operator()(uint8_t *ptr) const {
        heap_caps_free(ptr);
    }
};

using FrameBufferPtr = std::unique_ptr<uint8_t[], FrameBufferDeleter>;

const size_t frame_size = 320 * 240 * 2; // Формат RGB565 QVGA
FrameBufferPtr fb0(static_cast<uint8_t *>(heap_caps_malloc(frame_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_DMA)));
FrameBufferPtr fb1(static_cast<uint8_t *>(heap_caps_malloc(frame_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_DMA)));

if (!fb0 || !fb1) {
    // Обробка помилки нестачі пам'яті в PSRAM
}
