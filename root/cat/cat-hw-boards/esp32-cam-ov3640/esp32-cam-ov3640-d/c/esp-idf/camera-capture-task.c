#include "esp_camera.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "ov3640_config";

// Повна конфігурація розпіновки та параметрів для камери OV3640
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

    .xclk_freq_hz = 20000000,           // Частота XCLK 20 МГц для високого FPS
    .ledc_timer   = LEDC_TIMER_0,
    .ledc_channel = LEDC_CHANNEL_0,

    .pixel_format = PIXFORMAT_JPEG,     // Апаратне стиснення JPEG
    .frame_size   = FRAMESIZE_UXGA,     // Роздільна здатність UXGA (1600x1200)
    .jpeg_quality = 12,                 // Оптимальний баланс якості та розміру кадру
    .fb_count     = 2,                  // Подвійна буферизація
    .grab_mode    = CAMERA_GRAB_LATEST, // Захоплення найновішого свіжого кадру
    .fb_location  = CAMERA_FB_IN_PSRAM  // Виділення кадрових буферів у PSRAM
};

// Задача захоплення та обробки кадрів у FreeRTOS
void camera_capture_task(void *pvParameters) {
    esp_err_t err = esp_camera_init(&camera_config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації драйвера камери: 0x%x", err);
        vTaskDelete(NULL);
        return;
    }
    ESP_LOGI(TAG, "Драйвер камери OV3640 успішно ініціалізовано");

    while (1) {
        // Отримання вказівника на кадровий буфер із DMA/PSRAM
        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb) {
            ESP_LOGE(TAG, "Не вдалося отримати кадровий буфер");
            vTaskDelay(pdMS_TO_TICKS(100));
            continue;
        }

        // Обробка кадру (передача у сокет HTTP або запис на SDMMC)
        ESP_LOGI(TAG, "Захоплено кадр JPEG: %u байтів, ширина: %u, висота: %u",
                 fb->len, fb->width, fb->height);

        // Обов'язкове повернення кадрового буфера у кільцевий список DMA
        esp_camera_fb_return(fb);

        // Затримка між кадрами для запобігання перевантаженню процесора
        vTaskDelay(pdMS_TO_TICKS(30));
    }
}
