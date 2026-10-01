#include "esp_log.h"
#include "esp_camera.h"

static const char *TAG = "camera_main";

esp_err_t init_video_subsystem(const camera_config_t *config) {
    // Ініціалізація драйвера камери
    esp_err_t err = esp_camera_init(config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації камери: 0x%x", err);
        return err;
    }

    // Отримання вказівника на об'єкт керування сенсором
    sensor_t *s = esp_camera_sensor_get();
    if (s != NULL) {
        ESP_LOGI(TAG, "Сенсор виявлено, ID: 0x%x", s->id.PID);
    }
    return ESP_OK;
}
