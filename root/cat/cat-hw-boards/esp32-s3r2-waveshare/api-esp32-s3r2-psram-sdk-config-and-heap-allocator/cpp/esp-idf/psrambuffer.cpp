#include <cstdio>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "PSRAM_ALLOC_CPP";

class PsramBuffer {
public:
    explicit PsramBuffer(std::size_t size) : size_(size), data_(nullptr) {
        data_ = static_cast<std::uint8_t*>(heap_caps_malloc(size_, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
        if (!data_) {
            ESP_LOGE(TAG, "Помилка виділення %zu байтів у PSRAM", size_);
        } else {
            ESP_LOGI(TAG, "Виділено буфер у PSRAM за адресою %p", static_cast<void*>(data_));
        }
    }

    ~PsramBuffer() {
        if (data_) {
            heap_caps_free(data_);
        }
    }

    std::uint8_t* get() const { return data_; }

private:
    std::size_t size_;
    std::uint8_t *data_;
};
