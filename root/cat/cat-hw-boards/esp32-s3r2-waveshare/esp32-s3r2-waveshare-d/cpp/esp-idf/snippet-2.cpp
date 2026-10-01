#include <cstdio>
#include <cstddef>
#include <cstdint>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "main_cpp";

extern "C" void app_main(void)
{
    // Виділення кадрового буфера в PSRAM для C++
    const std::size_t buffer_size = 1600 * 1200 * 2; // UXGA RGB565
    auto *frame_buffer = static_cast<std::uint8_t *>(heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));

    if (frame_buffer == nullptr) {
        ESP_LOGE(TAG, "Не вдалося виділити буфер у PSRAM!");
        return;
    }

    ESP_LOGI(TAG, "Буфер у PSRAM успішно виділено за адресою: %p", static_cast<void *>(frame_buffer));

    // Звільнення пам'яті
    heap_caps_free(frame_buffer);
}
