#include <iostream>
#include <vector>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "PSRAM_CPP";

class PsramBuffer {
public:
    explicit PsramBuffer(size_t size) : size_(size), ptr_(nullptr) {
        ptr_ = static_cast<uint8_t *>(heap_caps_malloc(size_, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
        if (!ptr_) {
            ESP_LOGE(TAG, "Помилка виділення PSRAM обсягом %zu байтів", size_);
        }
    }

    ~PsramBuffer() {
        if (ptr_) {
            heap_caps_free(ptr_);
        }
    }

    uint8_t* data() { return ptr_; }
    size_t size() const { return size_; }

private:
    size_t size_;
    uint8_t *ptr_;
};
