#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "camera_dma";

// Конфігурація розпіновки DVP та параметрів буферизації
static camera_config_t camera_config = {
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

    .xclk_freq_hz = 20000000,           // Частота XCLK 20 МГц
    .ledc_timer   = LEDC_TIMER_0,
    .ledc_channel = LEDC_CHANNEL_0,

    .pixel_format = PIXFORMAT_JPEG,     // Апаратний формат JPEG
    .frame_size   = FRAMESIZE_SVGA,     // Роздільність SVGA (800x600)
    .jpeg_quality = 12,                 // Якість JPEG (12: висока якість, помірне стиснення)
    .fb_count     = 2,                  // Подвійна буферизація у PSRAM
    .grab_mode    = CAMERA_GRAB_LATEST, // Режим захоплення найновішого кадру
    .fb_location  = CAMERA_FB_IN_PSRAM  // Розміщення буферів у PSRAM
};

esp_err_t init_and_capture_dma(void) {
    // Ініціалізація драйвера камери
    esp_err_t err = esp_camera_init(&camera_config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації камери: 0x%x", err);
        return err;
    }

    // Неблокуюче отримання кадру з кільцевого буфера DMA
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGE(TAG, "Помилка захоплення кадрового буфера");
        return ESP_FAIL;
    }

    ESP_LOGI(TAG, "Захоплено кадр JPEG: %u байтів, %ux%u", 
             fb->len, fb->width, fb->height);

    // Повернення буфера у кільцеву чергу DMA для наступного кадру
    esp_camera_fb_return(fb);
    return ESP_OK;
}
