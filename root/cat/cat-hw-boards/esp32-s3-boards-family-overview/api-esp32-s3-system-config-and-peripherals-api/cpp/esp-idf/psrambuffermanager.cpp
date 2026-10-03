#include <cstdio>
#include <cstdint>
#include "esp_heap_caps.h"
#include "esp_log.h"

class PsramBufferManager {
private:
    static constexpr const char *TAG = "psram_cpp";
    uint8_t *buffer_ptr = nullptr;
    size_t size = 0;

public:
    explicit PsramBufferManager(size_t buffer_bytes) : size(buffer_bytes) {
        buffer_ptr = static_cast<uint8_t *>(heap_caps_malloc(size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
        if (!buffer_ptr) {
            ESP_LOGE(TAG, "Помилка виділення PSRAM буфера");
        } else {
            ESP_LOGI(TAG, "Виділено буфер PSRAM розміром %zu байт", size);
        }
    }

    ~PsramBufferManager() {
        if (buffer_ptr) {
            heap_caps_free(buffer_ptr);
            ESP_LOGI(TAG, "Пам'ять PSRAM вивільнено");
        }
    }

    uint8_t* get() const { return buffer_ptr; }
};
