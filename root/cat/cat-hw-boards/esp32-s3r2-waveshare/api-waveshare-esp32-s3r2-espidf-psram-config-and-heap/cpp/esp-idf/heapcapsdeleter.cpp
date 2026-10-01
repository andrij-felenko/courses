#include <cstdio>
#include <memory>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "PSRAM_CPP";

struct HeapCapsDeleter {
    void operator()(void *ptr) const {
        heap_caps_free(ptr);
    }
};

void allocate_cpp_example() {
    size_t psram_bytes = 1024 * 512;
    std::unique_ptr<uint8_t[], HeapCapsDeleter> frame_buffer(
        static_cast<uint8_t*>(heap_caps_malloc(psram_bytes, MALLOC_CAP_SPIRAM))
    );

    if (!frame_buffer) {
        ESP_LOGE(TAG, "Помилка виділення PSRAM в C++");
        return;
    }

    ESP_LOGI(TAG, "Об'єкт у C++ успішно розміщено в PSRAM: %p", frame_buffer.get());
}
