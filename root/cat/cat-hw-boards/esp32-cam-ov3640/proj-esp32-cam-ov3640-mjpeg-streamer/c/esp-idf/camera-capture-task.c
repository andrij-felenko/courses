#include "esp_camera.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"

// Конфігурація камери з подвійною буферизацією в PSRAM
static camera_config_t camera_config = {
    .pin_pwdn     = 32,
    .pin_reset    = -1,
    .pin_xclk     = 0,
    .pin_sscb_sda = 26,
    .pin_sscb_scl = 27,

    .pin_d7 = 35, .pin_d6 = 34, .pin_d5 = 39, .pin_d4 = 36,
    .pin_d3 = 19, .pin_d2 = 18, .pin_d1 = 5,  .pin_d0 = 4,
    .pin_vsync = 25, .pin_href = 23, .pin_pclk = 22,

    .xclk_freq_hz = 20000000,
    .ledc_timer   = LEDC_TIMER_0,
    .ledc_channel = LEDC_CHANNEL_0,

    .pixel_format = PIXFORMAT_JPEG,
    .frame_size   = FRAMESIZE_VGA,
    .jpeg_quality = 12,
    .fb_count     = 2,                     // Виділення двох кадрових буферів
    .fb_location  = CAMERA_FB_IN_PSRAM,    // Буфери розміщуються у PSRAM
    .grab_mode    = CAMERA_GRAB_LATEST     // Захоплення найсвіжішого кадру
};

// Задача захоплення кадрів
void camera_capture_task(void *pvParameters) {
    esp_err_t err = esp_camera_init(&camera_config);
    if (err != ESP_OK) {
        vTaskDelete(NULL);
        return;
    }

    while (1) {
        // Отримання готового кадру з буфера PSRAM
        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb) {
            vTaskDelay(pdMS_TO_TICKS(10));
            continue;
        }

        // Повернення буфера у вільний пул після використання
        esp_camera_fb_return(fb);
    }
}
