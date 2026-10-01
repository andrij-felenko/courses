#include <cstdio>
#include <cstring>
#include "esp_heap_caps.h"
#include "esp_log.h"

class FrameBuffer {
private:
    uint8_t *buffer_ptr;
    size_t buffer_size;
    static constexpr const char *TAG = "CPP_PSRAM";

public:
    explicit FrameBuffer(size_t size) : buffer_ptr(nullptr), buffer_size(size) {
        // Запит пам'яті в PSRAM із нульовою ініціалізацією
        buffer_ptr = static_cast<uint8_t*>(heap_caps_calloc(1, buffer_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
        if (!buffer_ptr) {
            ESP_LOGE(TAG, "Помилка виділення обсягу %zu байтів у PSRAM", buffer_size);
        } else {
            ESP_LOGI(TAG, "Об'єкт у PSRAM створено за адресою %p", buffer_ptr);
        }
    }

    ~FrameBuffer() {
        if (buffer_ptr) {
            heap_caps_free(buffer_ptr);
            ESP_LOGI(TAG, "Пам'ять PSRAM звільнено об'єктом");
        }
    }

    bool is_valid() const { return buffer_ptr != nullptr; }
    uint8_t* get() { return buffer_ptr; }
};
