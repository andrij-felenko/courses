#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "camera_init";

esp_err_t init_ov3640_camera(void) {
    camera_config_t config = {
        .pin_pwdn     = 32,
        .pin_reset    = -1,
        .pin_xclk     = 0,
        .pin_sscb_sda = 26,
        .pin_sscb_scl = 27,
        .pin_d7       = 35,
        .pin_d6       = 34,
        .pin_d5       = 39,
        .pin_d4       = 36,
        .pin_d3       = 21,
        .pin_d2       = 19,
        .pin_d1       = 18,
        .pin_d0       = 5,
        .pin_vsync    = 25,
        .pin_href     = 23,
        .pin_pclk     = 22,

        .xclk_freq_hz = 20000000,           // Тактова частота XVCLK 20 МГц для стабільного PCLK
        .ledc_timer   = LEDC_TIMER_0,
        .ledc_channel = LEDC_CHANNEL_0,

        .pixel_format = PIXFORMAT_JPEG,      // Використання апаратного кодека JPEG
        .frame_size   = FRAMESIZE_UXGA,      // Роздільність 1600x1200
        .jpeg_quality = 12,                  // Фактор квантування (10-15 для UXGA)
        .fb_count     = 2,                   // Подвійна буферизація у PSRAM
        .grab_mode    = CAMERA_GRAB_LATEST,  // Захоплення найновішого кадру проти затримок
        .fb_location  = CAMERA_FB_IN_PSRAM   // Розміщення кадрових масивів у PSRAM
    };

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації сенсора OV3640: 0x%x", err);
        return err;
    }
    return ESP_OK;
}
