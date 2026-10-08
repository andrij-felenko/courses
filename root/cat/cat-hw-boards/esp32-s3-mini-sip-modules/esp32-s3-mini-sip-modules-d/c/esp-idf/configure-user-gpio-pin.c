#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_err.h"

static const char *TAG = "SIP_SAFETY";

// Перевірка безпеки призначення GPIO для SiP-модуля ESP32-S3-MINI-1
esp_err_t configure_user_gpio_pin(gpio_num_t gpio_num) {
    // Виводи GPIO33-GPIO37 виділені під внутрішню шину Quad SPI Flash
    if (gpio_num >= GPIO_NUM_33 && gpio_num <= GPIO_NUM_37) {
        ESP_LOGE(TAG, "Критична помилка: GPIO%d зайнято внутрішньою SiP-пам'яттю Flash!", gpio_num);
        return ESP_ERR_INVALID_ARG;
    }

    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << gpio_num),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };

    return gpio_config(&io_conf);
}
