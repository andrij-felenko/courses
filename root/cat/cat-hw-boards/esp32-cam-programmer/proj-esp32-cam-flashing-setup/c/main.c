#include <stdio.h>
#include "esp_log.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_camera.h"
#include "camera_pins.h"

static const char *TAG = "main_c";

// Ініціалізація та налаштування конфігурації камери OV2640
static esp_err_t init_camera(void) {
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = CAM_PIN_D0;
    config.pin_d1 = CAM_PIN_D1;
    config.pin_d2 = CAM_PIN_D2;
    config.pin_d3 = CAM_PIN_D3;
    config.pin_d4 = CAM_PIN_D4;
    config.pin_d5 = CAM_PIN_D5;
    config.pin_d6 = CAM_PIN_D6;
    config.pin_d7 = CAM_PIN_D7;
    config.pin_xclk = CAM_PIN_XCLK;
    config.pin_pclk = CAM_PIN_PCLK;
    config.pin_vsync = CAM_PIN_VSYNC;
    config.pin_href = CAM_PIN_HREF;
    config.pin_sscb_sda = CAM_PIN_SIOD;
    config.pin_sscb_scl = CAM_PIN_SIOC;
    config.pin_pwdn = CAM_PIN_PWDN;
    config.pin_reset = CAM_PIN_RESET;
    config.xclk_freq_hz = 20000000; // 20 МГц для стабільного тактування камери
    config.pixel_format = PIXFORMAT_JPEG; // Формат JPEG для економії пам'яті

    // Вибір роздільної здатності залежно від наявності зовнішньої PSRAM
    if (psramFound()) {
        config.frame_size = FRAMESIZE_UXGA; // 1600x1200
        config.jpeg_quality = 10;           // Якість JPEG (0-63, менше = краще)
        config.fb_count = 2;                 // Подвійна буферизація в PSRAM
        config.grab_mode = CAMERA_GRAB_LATEST;
        ESP_LOGI(TAG, "Виявлено PSRAM: встановлено роздільну здатність UXGA");
    } else {
        config.frame_size = FRAMESIZE_SVGA; // 800x600 без PSRAM
        config.jpeg_quality = 12;
        config.fb_count = 1;
        config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
        ESP_LOGW(TAG, "PSRAM не знайдено: обмежено роздільну здатність до SVGA");
    }

    // Низькорівневий запуск драйвера камери
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації камери esp_camera_init: 0x%x (%s)", err, esp_err_to_name(err));
        return err;
    }

    ESP_LOGI(TAG, "Драйвер камери успішно ініціалізовано");
    return ESP_OK;
}

void app_main(void) {
    ESP_LOGI(TAG, "Запуск C-прошивки для ESP32-CAM");

    // Запуск конфігурації та драйвера камери
    if (init_camera() != ESP_OK) {
        ESP_LOGE(TAG, "Критична помилка запуску камери, зупинка роботи");
        return;
    }

    uint32_t frame_counter = 0;

    // Головний цикл захоплення кадрів
    while (1) {
        frame_counter++;
        ESP_LOGI(TAG, "Спроба отримання кадру #%lu...", (unsigned long)frame_counter);

        // Отримання буфера кадру від сенсора
        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb) {
            ESP_LOGE(TAG, "Не вдалося отримати фреймбуфер від камери");
            vTaskDelay(pdMS_TO_TICKS(2000));
            continue;
        }

        // Вивід параметрів отриманого зображення
        ESP_LOGI(TAG, "Успішно захоплено кадр #%lu: розмір = %zu байт, ширина = %d, висота = %d, формат = %d",
                 (unsigned long)frame_counter, fb->len, fb->width, fb->height, fb->format);

        // Обов'язкове повернення буфера пам'яті драйверу для запобігання витокам
        esp_camera_fb_return(fb);
        fb = NULL;

        // Затримка 1 секунда перед наступним захопленням
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
