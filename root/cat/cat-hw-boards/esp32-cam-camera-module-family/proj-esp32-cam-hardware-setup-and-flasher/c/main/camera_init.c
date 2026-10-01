#include <stdio.h>
#include "esp_log.h"
#include "esp_camera.h"
#include "esp_psram.h"
#include "camera_pins.h"

static const char *TAG = "camera_init";

/**
 * @brief Налаштування конфігурації та ініціалізація драйвера камери esp_camera
 * @return esp_err_t ESP_OK у разі успіху, або код помилки
 */
esp_err_t init_camera(void)
{
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;

    // Перевірка наявності PSRAM для вибору роздільності та подвійної буферизації
    if (esp_psram_is_initialized()) {
        config.frame_size = FRAMESIZE_UXGA; // 1600x1200
        config.jpeg_quality = 10;           // 0-63, менше значення = вища якість
        config.fb_count = 2;                // Подвійна буферизація в PSRAM
        config.grab_mode = CAMERA_GRAB_LATEST;
        ESP_LOGI(TAG, "Зовнішню пам'ять PSRAM виявлено. Налаштовано подвійну буферизацію UXGA.");
    } else {
        config.frame_size = FRAMESIZE_SVGA; // 800x600 для внутрішньої DRAM
        config.jpeg_quality = 12;
        config.fb_count = 1;
        config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
        ESP_LOGW(TAG, "PSRAM не виявлено! Обмежено роздільність до SVGA та 1 кадрову буферизацію.");
    }

    // Ініціалізація драйвера камери
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації камери: 0x%x", err);
        return err;
    }

    ESP_LOGI(TAG, "Драйвер камери успішно ініціалізовано.");
    return ESP_OK;
}
