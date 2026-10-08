#include "esp_camera.h"
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "cam_init";

esp_err_t init_camera_octal_psram(void) {
    camera_config_t config = {
        .pin_pwdn = -1,
        .pin_reset = -1,
        .pin_xclk = 10,
        .pin_sccb_sda = 40,
        .pin_sccb_scl = 39,
        .pin_d7 = 48,
        .pin_d6 = 11,
        .pin_d5 = 12,
        .pin_d4 = 14,
        .pin_d3 = 16,
        .pin_d2 = 18,
        .pin_d1 = 17,
        .pin_d0 = 15,
        .pin_vsync = 38,
        .pin_href = 47,
        .pin_pclk = 13,
        .xclk_freq_hz = 20000000,
        .ledc_timer = LEDC_TIMER_0,
        .ledc_channel = LEDC_CHANNEL_0,
        .pixel_format = PIXFORMAT_RGB565,
        .frame_size = FRAMESIZE_SVGA,
        .jpeg_quality = 12,
        .fb_count = 2,
        .grab_mode = CAMERA_GRAB_LATEST,
        .fb_location = CAMERA_FB_IN_PSRAM
    };

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації камери: 0x%x", err);
        return err;
    }
    ESP_LOGI(TAG, "Камера успішно ініціалізована у Octal SPI PSRAM");
    return ESP_OK;
}
