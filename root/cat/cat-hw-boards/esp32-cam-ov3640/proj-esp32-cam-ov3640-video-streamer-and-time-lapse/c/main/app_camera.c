#include "app_camera.h"
#include "esp_log.h"

static const char *TAG = "APP_CAMERA";

esp_err_t app_camera_init(void) {
    camera_config_t config = {
        .ledc_channel = LEDC_CHANNEL_0,
        .ledc_timer   = LEDC_TIMER_0,
        .pin_d0       = CAM_PIN_D0,
        .pin_d1       = CAM_PIN_D1,
        .pin_d2       = CAM_PIN_D2,
        .pin_d3       = CAM_PIN_D3,
        .pin_d4       = CAM_PIN_D4,
        .pin_d5       = CAM_PIN_D5,
        .pin_d6       = CAM_PIN_D6,
        .pin_d7       = CAM_PIN_D7,
        .pin_xclk     = CAM_PIN_XCLK,
        .pin_pclk     = CAM_PIN_PCLK,
        .pin_vsync    = CAM_PIN_VSYNC,
        .pin_href     = CAM_PIN_HREF,
        .pin_siod     = CAM_PIN_SIOD,
        .pin_sioc     = CAM_PIN_SIOC,
        .pin_pwdn     = CAM_PIN_PWDN,
        .pin_reset    = CAM_PIN_RESET,
        .xclk_freq_hz = 20000000,
        .pixel_format = PIXFORMAT_JPEG,
        .frame_size   = FRAMESIZE_UXGA, // Роздільна здатність 2 МП для OV3640
        .jpeg_quality = 10,
        .fb_count     = 2,              // Подвійний буфер у PSRAM
        .grab_mode    = CAMERA_GRAB_LATEST
    };

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації камери OV3640: 0x%x", err);
        return err;
    }

    ESP_LOGI(TAG, "Камеру OV3640 успішно ініціалізовано в режимі UXGA");
    return ESP_OK;
}

camera_fb_t* app_camera_take_picture(void) {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGE(TAG, "Захоплення кадру не вдалося");
        return NULL;
    }
    return fb;
}

void app_camera_release_picture(camera_fb_t *fb) {
    if (fb) {
        esp_camera_fb_return(fb);
    }
}
