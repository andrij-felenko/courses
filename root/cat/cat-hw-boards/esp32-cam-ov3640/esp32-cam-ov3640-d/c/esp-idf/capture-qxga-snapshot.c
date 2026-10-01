#include "esp_camera.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "camera_control";

// Динамічна конфігурація регістрів та безпечний цикл захоплення кадру
void capture_qxga_snapshot(void) {
    sensor_t *s = esp_camera_sensor_get();
    if (!s) {
        ESP_LOGE(TAG, "Сенсор камери не знайдено!");
        return;
    }

    // Встановлення режимів обробки зображення через SCCB
    s->set_whitebal(s, 1);       // Увімкнення автобалансу білого
    s->set_exposure_ctrl(s, 1);  // Увімкнення автоекспозиції
    s->set_hmirror(s, 0);        // Вимкнення дзеркального відображення

    // Динамічне перемикання на високу роздільну здатність UXGA
    s->set_framesize(s, FRAMESIZE_UXGA);
    vTaskDelay(pdMS_TO_TICKS(150)); // Пауза для стабілізації PLL сенсора

    // Захоплення кадру через DMA
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGE(TAG, "Помилка захоплення кадру з шини DVP!");
        return;
    }

    ESP_LOGI(TAG, "Кадр захоплено успішно! Розмір: %u байт", fb->len);

    // Обов'язкове повернення буфера у масив PSRAM для розблокування DMA
    esp_camera_fb_return(fb);
}
