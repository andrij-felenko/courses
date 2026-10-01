#include <cstdio>
#include <cstdint>
#include <memory>
#include "esp_log.h"
#include "esp_heap_caps.h"

static const char *TAG = "PSRAM_CPP_DEMO";

struct PsramDeleter {
    void operator()(void *ptr) const {
        if (ptr != nullptr) {
            heap_caps_free(ptr);
        }
    }
};

extern "C" void app_main(void)
{
    constexpr std::size_t buffer_size = 512 * 1024; // 512 КБ під кадровий буфер

    std::unique_ptr<std::uint8_t[], PsramDeleter> psram_buffer(
        static_cast<std::uint8_t *>(heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM))
    );

    if (!psram_buffer) {
        ESP_LOGE(TAG, "Не вдалося виділити пам'ять у PSRAM через C++ API!");
        return;
    }

    ESP_LOGI(TAG, "Успішно виділено %zu байтів у PSRAM під управлінням RAII", buffer_size);

    for (std::size_t i = 0; i < buffer_size; ++i) {
        psram_buffer[i] = static_cast<std::uint8_t>(i & 0xFF);
    }

    // Автоматичне звільнення пам'яті через кастомний видаляч RAII
}
