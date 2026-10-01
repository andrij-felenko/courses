#include "esp_camera.h"
#include "esp_log.h"

namespace {
constexpr const char *TAG = "camera_diag_cpp";
}

esp_err_t init_camera_with_fallback_cpp(camera_config_t &config)
{
    esp_err_t err = esp_camera_init(&config);
    if (err == ESP_ERR_NOT_FOUND) {
        ESP_LOGE(TAG, "OV3640 відсутній на SCCB: перевірте підтяжку резисторами та DOVDD");
        return err;
    } else if (err == ESP_ERR_NO_MEM) {
        ESP_LOGE(TAG, "Помилка виділення пам'яті в PSRAM");
        return err;
    } else if (err != ESP_OK) {
        ESP_LOGW(TAG, "Зниження частоти XCLK до 10 МГц через помилку 0x%x", err);
        config.xclk_freq_hz = 10000000;
        err = esp_camera_init(&config);
    }

    if (err == ESP_OK) {
        ESP_LOGI(TAG, "Драйвер камери запущено на частоті %d МГц", config.xclk_freq_hz / 1000000);
    }
    return err;
}
