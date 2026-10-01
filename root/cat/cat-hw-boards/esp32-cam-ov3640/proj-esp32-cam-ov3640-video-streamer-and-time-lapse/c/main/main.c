#include <stdio.h>
#include "esp_log.h"
#include "esp_sleep.h"
#include "nvs_flash.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "app_camera.h"

static const char *TAG = "MAIN";

// Змінна лічильника кадрів у пам'яті RTC Fast Memory (зберігається при Deep Sleep)
static RTC_DATA_ATTR uint32_t s_photo_count = 0;

// Оголошення функцій із зовнішніх модулів
esp_err_t app_sdcard_init(void);
esp_err_t app_sdcard_save_photo(const uint8_t *data, size_t len, uint32_t photo_num);
void app_httpd_start_stream(void);

void app_main(void) {
    ESP_LOGI(TAG, "--- Пробудження ESP32-CAM. Знімок №%lu ---", (unsigned long)s_photo_count);

    // Крок 1. Ініціалізація NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    // Крок 2. Ініціалізація камери OV3640
    if (app_camera_init() != ESP_OK) {
        ESP_LOGE(TAG, "Збій старту камери. Перехід у сон");
        esp_deep_sleep(10 * 1000000LL); // 10 секунд
    }

    // Крок 3. Ініціалізація SD-картки та збереження кадру
    if (app_sdcard_init() == ESP_OK) {
        camera_fb_t *fb = app_camera_take_picture();
        if (fb) {
            app_sdcard_save_photo(fb->buf, fb->len, s_photo_count++);
            app_camera_release_picture(fb);
        }
    }

    // Крок 4. Запуск HTTP MJPEG потоку
    app_httpd_start_stream();

    // Крок 5. Конфігурування таймера Deep Sleep на 30 секунд
    ESP_LOGI(TAG, "Перехід у режим Deep Sleep на 30 секунд...");
    esp_sleep_enable_timer_wakeup(30 * 1000000LL);
    
    // Затримка перед сном для завершення виводу логів
    vTaskDelay(pdMS_TO_TICKS(100));
    esp_deep_sleep_start();
}
