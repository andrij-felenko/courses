#include "esp_camera.h"
#include "esp_log.h"
#include "esp_task_wdt.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "cam_guard";

// Завдання опитування камери з контролем сторожового таймера TWDT
void camera_capture_task(void *pvParameters) {
    // Реєстрація поточного завдання у сторожовому таймері TWDT
    esp_task_wdt_add(NULL);

    while (1) {
        // Скидання сторожового таймера для підтвердження нормальної роботи
        esp_task_wdt_reset();

        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb) {
            ESP_LOGE(TAG, "Помилка захоплення кадру: тайм-аут DMA або збій шини");
            // Переініціалізація драйвера камери у разі апаратного збою
            esp_camera_deinit();
            vTaskDelay(pdMS_TO_TICKS(100));
            // Відновлення роботи драйвера камери
            if (esp_camera_init((camera_config_t*)pvParameters) != ESP_OK) {
                ESP_LOGE(TAG, "Критична помилка: не вдалося перезапустити камеру, перезавантаження МК");
                esp_restart();
            }
            continue;
        }

        // Успішна обробка кадрового буфера
        esp_camera_fb_return(fb);
        vTaskDelay(pdMS_TO_TICKS(30));
    }
}
