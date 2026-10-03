#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "sensor_ctrl";

void configure_ov3640_low_light(void) {
    sensor_t *s = esp_camera_sensor_get();
    if (!s) {
        ESP_LOGE(TAG, "Вказівник на sensor_t не знайдено");
        return;
    }

    // Увімкнення автоматичної експозиції та підсилення
    s->set_exposure_ctrl(s, 1);
    s->set_gain_ctrl(s, 1);
    s->set_gainceiling(s, GAINCEILING_16X);

    // Налаштування балансу білого
    s->set_whitebal(s, 1);
    s->set_wb_mode(s, 0); // 0: Auto

    // Корекція орієнтації кадру
    s->set_hmirror(s, 1);
    s->set_vflip(s, 1);
}
