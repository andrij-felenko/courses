#include "esp_camera.h"
#include "esp_log.h"
#include "esp_system.h"

static const char *TAG = "camera_psram";

// Перевірка наявності PSRAM та конфігурація подвійної буферизації
esp_err_t init_camera_buffers(void) {
    if (!esp_psram_is_initialized()) {
        ESP_LOGE(TAG, "Помилка: Зовнішня PSRAM не знайдена на платі!");
        return ESP_FAIL;
    }

    camera_config_t config = {
        .pin_pwdn     = 32,
        .pin_reset    = -1,
        .pin_xclk     = 0,
        .pin_sccb_sda = 26,
        .pin_sccb_scl = 27,
        .pin_d7 = 35, .pin_d6 = 34, .pin_d5 = 39, .pin_d4 = 36,
        .pin_d3 = 21, .pin_d2 = 19, .pin_d1 = 18, .pin_d0 = 5,
        .pin_vsync = 25, .pin_href = 23, .pin_pclk = 22,
        .xclk_freq_hz = 20000000,
        .pixel_format = PIXFORMAT_JPEG,
        .frame_size   = FRAMESIZE_QXGA,
        .jpeg_quality = 12, // Оптимальний баланс розміру кадру (180-250 КБ)
        .fb_count     = 2,  // Виділення двох буферів у PSRAM
        .grab_mode    = CAMERA_GRAB_LATEST
    };

    return esp_camera_init(&config);
}
