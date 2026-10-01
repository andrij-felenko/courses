#include <iostream>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "MAIN_CPP";

extern "C" void app_main(void)
{
    // Виділення кадрового буфера у зовнішній PSRAM мовою C++
    std::size_t frame_buffer_size = 640 * 480 * 2;
    auto *fb_psram = static_cast<uint8_t *>(heap_caps_malloc(frame_buffer_size, MALLOC_CAP_SPIRAM));

    if (fb_psram == nullptr) {
        ESP_LOGE(TAG, "Не вдалося виділити пам'ять у PSRAM!");
    } else {
        ESP_LOGI(TAG, "Успішно виділено %d байт у зовнішній PSRAM", static_cast<int>(frame_buffer_size));
        heap_caps_free(fb_psram);
    }
}
