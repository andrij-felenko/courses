#include "esp_camera.h"
#include "esp_log.h"
#include "esp_heap_caps.h"

static const char *TAG = "camera_diag";

esp_err_t init_and_capture(const camera_config_t *config) {
    // Перевіряємо наявність зовнішньої пам'яті PSRAM перед викликом
    if (heap_caps_get_free_size(MALLOC_CAP_SPIRAM) < (1024 * 1024)) {
        ESP_LOGE(TAG, "Недостатньо вільної PSRAM для буферів");
        return ESP_ERR_NO_MEM;
    }

    esp_err_t err = esp_camera_init(config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації камери: 0x%x", err);
        return err;
    }

    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGE(TAG, "Не вдалося захопити кадр");
        return ESP_FAIL;
    }

    // Обробка кадру...

    // Обов'язкове вивільнення буфера для запобігання витокам пам'яті
    esp_camera_fb_return(fb);
    return ESP_OK;
}
