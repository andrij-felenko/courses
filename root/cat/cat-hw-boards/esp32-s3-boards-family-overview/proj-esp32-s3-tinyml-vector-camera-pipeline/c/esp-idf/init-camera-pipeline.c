#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "camera_dma";

// Конфігурація шини LCD_CAM та контролера GDMA
static camera_config_t cam_config = {
    .pin_pwdn     = -1,
    .pin_reset    = -1,
    .pin_xclk     = 10,
    .pin_sccb_sda = 40,
    .pin_sccb_scl = 39,

    .pin_d7       = 35,
    .pin_d6       = 36,
    .pin_d5       = 37,
    .pin_d4       = 38,
    .pin_d3       = 4,
    .pin_d2       = 5,
    .pin_d1       = 6,
    .pin_d0       = 7,
    .pin_vsync    = 8,
    .pin_href     = 9,
    .pin_pclk     = 11,

    .xclk_freq_hz = 20000000,
    .ledc_timer   = LEDC_TIMER_0,
    .ledc_channel = LEDC_CHANNEL_0,

    .pixel_format = PIXFORMAT_RGB565,
    .frame_size   = FRAMESIZE_QVGA,

    .jpeg_quality = 12,
    .fb_count     = 2,                  // Двобуферний кільцевий режим DMA
    .grab_mode    = CAMERA_GRAB_LATEST,
    .fb_location  = CAMERA_FB_IN_PSRAM
};

esp_err_t init_camera_pipeline(void) {
    esp_err_t ret = esp_camera_init(&cam_config);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації LCD_CAM: 0x%x", ret);
        return ret;
    }
    ESP_LOGI(TAG, "Безперервний фоновий потік DMA успішно запущено");
    return ESP_OK;
}
