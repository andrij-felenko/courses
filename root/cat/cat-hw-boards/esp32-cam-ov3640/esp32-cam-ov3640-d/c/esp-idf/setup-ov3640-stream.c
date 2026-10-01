#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "ov3640_init";

esp_err_t setup_ov3640_stream(void) {
    camera_config_t config = {
        .pin_pwdn = -1,
        .pin_reset = 15,
        .pin_xclk = 27,
        .pin_sscb_sda = 26,
        .pin_sscb_scl = 27,
        .pin_d7 = 35,
        .pin_d6 = 34,
        .pin_d5 = 39,
        .pin_d4 = 36,
        .pin_d3 = 19,
        .pin_d2 = 18,
        .pin_d1 = 5,
        .pin_d0 = 4,
        .pin_vsync = 25,
        .pin_href = 23,
        .pin_pclk = 22,
        .xclk_freq_hz = 20000000,
        .ledc_timer = LEDC_TIMER_0,
        .ledc_channel = LEDC_CHANNEL_0,
        .pixel_format = PIXFORMAT_JPEG,
        .frame_size = FRAMESIZE_UXGA,
        .jpeg_quality = 12,
        .fb_count = 2,
        .grab_mode = CAMERA_GRAB_LATEST
    };

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації сенсора OV3640: 0x%x", err);
        return err;
    }
    return ESP_OK;
}
