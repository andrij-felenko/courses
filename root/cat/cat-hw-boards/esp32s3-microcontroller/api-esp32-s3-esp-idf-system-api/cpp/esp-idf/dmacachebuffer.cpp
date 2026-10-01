#include <cstdint>
#include <cstring>
#include "esp_heap_caps.h"
#include "esp_cache.h"
#include "esp_check.h"

class DmaCacheBuffer {
public:
    static constexpr size_t kCacheLineSize = 32;

    explicit DmaCacheBuffer(size_t size) : size_(size) {
        buffer_ = static_cast<uint8_t*>(heap_caps_aligned_alloc(
            kCacheLineSize, size_, MALLOC_CAP_SPIRAM | MALLOC_CAP_DMA));
    }

    ~DmaCacheBuffer() {
        if (buffer_) {
            heap_caps_free(buffer_);
        }
    }

    uint8_t* data() { return buffer_; }
    size_t size() const { return size_; }

    esp_err_t sync_for_device() {
        if (!buffer_) return ESP_ERR_INVALID_STATE;
        // Виштовхування модифікованих даних із кешу в PSRAM
        return esp_cache_msync(buffer_, size_, ESP_CACHE_MSYNC_FLAG_DIR_C2M);
    }

private:
    uint8_t* buffer_{nullptr};
    size_t size_{0};
};
