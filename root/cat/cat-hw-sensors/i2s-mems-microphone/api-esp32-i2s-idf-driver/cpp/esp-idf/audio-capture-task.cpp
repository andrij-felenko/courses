#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2s_std.h"
#include "esp_log.h"
#include <array>

static const char *TAG = "I2S_MIC";

void audio_capture_task(void *pvParameters) {
    std::array<int32_t, 240> raw_samples;
    size_t bytes_read = 0;

    i2s_channel_enable(rx_handle);

    while (true) {
        esp_err_t err = i2s_channel_read(rx_handle, raw_samples.data(), raw_samples.size() * sizeof(int32_t), &bytes_read, pdMS_TO_TICKS(1000));
        
        if (err == ESP_OK) {
            size_t samples_count = bytes_read / sizeof(int32_t);
            for (size_t i = 0; i < samples_count; ++i) {
                int16_t pcm_16bit = static_cast<int16_t>(raw_samples[i] >> 14);
                (void)pcm_16bit;
            }
        } else if (err == ESP_ERR_TIMEOUT) {
            ESP_LOGW(TAG, "Таймаут I2S: буфер DMA порожній");
        } else {
            ESP_LOGE(TAG, "Помилка I2S: %s", esp_err_to_name(err));
            break;
        }
    }

    i2s_channel_disable(rx_handle);
    i2s_del_channel(rx_handle);
    vTaskDelete(nullptr);
}
