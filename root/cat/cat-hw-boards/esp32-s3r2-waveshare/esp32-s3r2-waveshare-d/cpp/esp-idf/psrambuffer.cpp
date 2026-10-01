#include <iostream>
#include <cstddef>
#include "esp_heap_caps.h"
#include "esp_log.h"

class PsramBuffer {
public:
    explicit PsramBuffer(size_t size) : size_(size), data_(nullptr) {
        // Запит пам'яті у зовнішній SiP PSRAM з підтримкою DMA
        data_ = static_cast<uint8_t*>(heap_caps_malloc(size_, MALLOC_CAP_SPIRAM | MALLOC_CAP_DMA));
        if (!data_) {
            ESP_LOGE("PsramBuffer", "Помилка виділення %zu байт у PSRAM", size_);
        }
    }

    ~PsramBuffer() {
        if (data_) {
            heap_caps_free(data_);
        }
    }

    uint8_t* data() const { return data_; }
    bool isValid() const { return data_ != nullptr; }

private:
    size_t size_;
    uint8_t* data_;
};
