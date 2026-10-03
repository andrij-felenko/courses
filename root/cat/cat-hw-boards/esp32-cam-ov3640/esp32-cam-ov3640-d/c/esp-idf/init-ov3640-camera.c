#include "esp_camera.h"
#include "esp_log.h"
#include "esp_psram.h"

static const char *TAG = "ov3640_config";

esp_err_t init_ov3640_camera(void) {
    camera_config_t config = {
        .pin_pwdn     = 32,
        .pin_reset    = -1,
        .pin_xclk     = 0,
        .pin_sccb_sda = 26,
        .pin_sccb_scl = 27,

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

        .xclk_freq_hz = 20000000,
        .ledc_timer   = LEDC_TIMER_0,
        .ledc_channel = LEDC_CHANNEL_0,

        .pixel_format = PIXFORMAT_JPEG,
        .frame_size   = FRAMESIZE_UXGA,
        .jpeg_quality = 10,
        .fb_count     = 2,
        .grab_mode    = CAMERA_GRAB_LATEST,
        .fb_location  = CAMERA_FB_IN_PSRAM
    };

    // Перевірка наявності PSRAM та динамічна адаптація параметрів
    if (!esp_psram_is_initialized()) {
        ESP_LOGW(TAG, "PSRAM не виявлено! Перехід у режим збереження пам'яті.");
        config.frame_size  = FRAMESIZE_SVGA;
        config.jpeg_quality = 15;
        config.fb_count    = 1;
        config.fb_location = CAMERA_FB_IN_DRAM;
    }

    // Ініціалізація апаратного драйвера камери
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації камери: 0x%x", err);
        return err;
    }

    // Підлаштування параметрів зображення через об'єкт сенсора
    sensor_t *s = esp_camera_sensor_get();
    if (s != NULL) {
        s->set_vflip(s, 1);
        s->set_hmirror(s, 1);
    }

    return ESP_OK;
}
