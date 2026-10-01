#include <stdio.h>
#include "esp_log.h"
#include "esp_camera.h"
#include "esp_psram.h"
#include "camera_pins.h"

static const char *TAG = "camera_init";

/**
 * @brief Ініціалізація драйвера камери esp_camera з урахуванням наявності PSRAM
 * @return esp_err_t ESP_OK у разі успіху, код помилки у разі збою
 */
esp_err_t init_camera_ov3640(void)
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

    // Оптимізація роздільності та кількості буферів кадру за наявністю PSRAM
    if (esp_psram_is_initialized()) {
        config.frame_size = FRAMESIZE_QXGA; // 2048x1536 для сенсора OV3640
        config.jpeg_quality = 12;            // Якість JPEG (0-63, менше = краща якість)
        config.fb_count = 2;                 // Подвійна буферизація в PSRAM
        config.grab_mode = CAMERA_GRAB_LATEST;
        ESP_LOGI(TAG, "PSRAM активна. Конфігурація: QXGA (3 МП), подвійна буферизація.");
    } else {
        config.frame_size = FRAMESIZE_SVGA;  // Обмеження до 800x600 без PSRAM
        config.jpeg_quality = 15;
        config.fb_count = 1;
        config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
        ESP_LOGW(TAG, "PSRAM відсутня! Роздільність обмежено до SVGA, 1 буфер.");
    }

    // Ініціалізація драйвера esp_camera
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації драйвера камери: 0x%x", err);
        return err;
    }

    ESP_LOGI(TAG, "Камеру OV3640 успішно ініціалізовано.");
    return ESP_OK;
}
