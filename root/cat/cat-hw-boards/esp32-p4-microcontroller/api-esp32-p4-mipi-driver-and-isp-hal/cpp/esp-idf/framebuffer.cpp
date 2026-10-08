#include <cstdio>
#include <cstddef>
#include <cstdint>
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_cache.h"

static const char *TAG = "video_buffer_cpp";

#ifndef SOC_CACHE_LINE_SIZE
#define SOC_CACHE_LINE_SIZE 64
#endif

// Клас-обгортка для безпечного керування ресурсами DMA кадрового буфера в PSRAM
class FrameBuffer {
public:
    FrameBuffer(size_t width, size_t height, size_t bytes_per_pixel)
        : m_width(width), m_height(height), m_bpp(bytes_per_pixel), m_data(nullptr), m_size(0) {
        size_t raw_size = m_width * m_height * m_bpp;
        m_size = (raw_size + SOC_CACHE_LINE_SIZE - 1) & ~(SOC_CACHE_LINE_SIZE - 1);

        m_data = static_cast<uint8_t*>(heap_caps_aligned_alloc(
            SOC_CACHE_LINE_SIZE,
            m_size,
            MALLOC_CAP_SPIRAM | MALLOC_CAP_DMA
        ));

        if (!m_data) {
            ESP_LOGE(TAG, "Помилка виділення PSRAM DMA-буфера розміром %zu байтів", m_size);
        }
    }

    ~FrameBuffer() {
        if (m_data) {
            heap_caps_free(m_data);
        }
    }

    // Заборона копіювання для запобігання подвійного звільнення пам'яті
    FrameBuffer(const FrameBuffer&) = delete;
    FrameBuffer& operator=(const FrameBuffer&) = delete;

    uint8_t* data() const { return m_data; }
    size_t size() const { return m_size; }
    bool is_valid() const { return m_data != nullptr; }

private:
    size_t m_width;
    size_t m_height;
    size_t m_bpp;
    uint8_t *m_data;
    size_t m_size;
};
