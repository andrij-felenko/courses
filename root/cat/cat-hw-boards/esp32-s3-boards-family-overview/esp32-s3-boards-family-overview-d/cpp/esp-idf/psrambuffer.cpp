#include <iostream>
#include "esp_heap_caps.h"
#include "esp_log.h"

class PsramBuffer {
private:
    uint8_t *data_;
    size_t size_;
    static constexpr const char *TAG = "PsramBuffer";

public:
    explicit PsramBuffer(size_t size) : data_(nullptr), size_(size) {
        // Алокація у зовнішній оперативній пам'яті PSRAM
        data_ = static_cast<uint8_t *>(heap_caps_malloc(size_, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
        if (!data_) {
            ESP_LOGE(TAG, "Не вдалося виділити %zu байт у PSRAM", size_);
        } else {
            ESP_LOGI(TAG, "Виділено буфер PSRAM обсягом %zu байт", size_);
        }
    }

    ~PsramBuffer() {
        if (data_) {
            heap_caps_free(data_);
            ESP_LOGI(TAG, "Очищено буфер PSRAM");
        }
    }

    uint8_t *get() const { return data_; }
    bool is_valid() const { return data_ != nullptr; }
};
