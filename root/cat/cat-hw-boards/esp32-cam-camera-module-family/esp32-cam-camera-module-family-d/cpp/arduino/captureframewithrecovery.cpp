#include "esp_camera.h"
#include "esp_task_wdt.h"

// Захоплення кадру з автоматичною повторною ініціалізацією камери під час збою
camera_fb_t* captureFrameWithRecovery(const camera_config_t* config) {
    // Скидаємо сторожовий таймер для запобігання системного перезавантаження
    esp_task_wdt_reset();

    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Помилка DMA буфера! Перезапуск драйвера камери...");
        esp_camera_deinit();
        delay(100);
        if (esp_camera_init(config) != ESP_OK) {
            Serial.println("Апаратний збій камери! Виконуємо системне перезавантаження...");
            ESP.restart();
        }
        return NULL;
    }
    return fb;
}
