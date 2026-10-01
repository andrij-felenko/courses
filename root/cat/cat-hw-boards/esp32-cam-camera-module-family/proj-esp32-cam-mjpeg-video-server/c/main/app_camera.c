#include "app_camera.h"
#include "esp_log.h"
#include "esp_psram.h"

static const char *TAG = "app_camera";

esp_err_t app_camera_init(void)
{
    camera_config_t config = {
        .pin_pwdn = CAM_PIN_PWDN,
        .pin_reset = CAM_PIN_RESET,
        .pin_xclk = CAM_PIN_XCLK,
        .pin_siod = CAM_PIN_SIOD,
        .pin_sioc = CAM_PIN_SIOC,

        .pin_d7 = CAM_PIN_D7,
        .pin_d6 = CAM_PIN_D6,
        .pin_d5 = CAM_PIN_D5,
        .pin_d4 = CAM_PIN_D4,
        .pin_d3 = CAM_PIN_D3,
        .pin_d2 = CAM_PIN_D2,
        .pin_d1 = CAM_PIN_D1,
        .pin_d0 = CAM_PIN_D0,
        .pin_vsync = CAM_PIN_VSYNC,
        .pin_href = CAM_PIN_HREF,
        .pin_pclk = CAM_PIN_PCLK,

        .xclk_freq_hz = 20000000,
        .ledc_timer = LEDC_TIMER_0,
        .ledc_channel = LEDC_CHANNEL_0,

        .pixel_format = PIXFORMAT_JPEG,
        .frame_size = FRAMESIZE_VGA,
        .jpeg_quality = 12,
        .fb_count = 1,
        .grab_mode = CAMERA_GRAB_WHEN_EMPTY,
        .fb_location = CAMERA_FB_IN_DRAM
    };

    // Перевіряємо доступність зовнішньої пам'яті PSRAM для оптимізації буферів
    if (esp_psram_is_initialized()) {
        ESP_LOGI(TAG, "Виявлено PSRAM: розширюємо фреймбуфер та роздільну здатність");
        config.frame_size = FRAMESIZE_SVGA;
        config.jpeg_quality = 10;
        config.fb_count = 2;
        config.fb_location = CAMERA_FB_IN_PSRAM;
    } else {
        ESP_LOGW(TAG, "PSRAM не виявлено: використовуємо обмежені DRAM-буфери");
        config.frame_size = FRAMESIZE_QVGA;
        config.fb_count = 1;
        config.fb_location = CAMERA_FB_IN_DRAM;
    }

    // Ініціалізація сенсора камери
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації камери: 0x%x", err);
        return err;
    }

    sensor_t *s = esp_camera_sensor_get();
    if (s != NULL) {
        // Оптимізуємо налаштування зображення сенсора OV2640
        s->set_vflip(s, 1);
        s->set_hmirror(s, 0);
    }

    ESP_LOGI(TAG, "Камеру OV2640 успішно ініціалізовано");
    return ESP_OK;
}
