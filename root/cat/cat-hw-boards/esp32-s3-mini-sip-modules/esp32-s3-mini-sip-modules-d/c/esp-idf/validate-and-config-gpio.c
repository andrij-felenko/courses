#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_err.h"

static const char *TAG = "PIN_ALLOC";

// Перевірка безпеки призначення GPIO для модуля ESP32-S3-MINI-1
esp_err_t validate_and_config_gpio(gpio_num_t pin, gpio_mode_t mode) {
    // Перевірка приватних виводів внутрішньої SiP-пам'яті Flash
    if (pin >= GPIO_NUM_33 && pin <= GPIO_NUM_37) {
        ESP_LOGE(TAG, "Помилка: GPIO%d є внутрішньою шиною Quad SPI Flash!", pin);
        return ESP_ERR_INVALID_ARG;
    }

    // Перевірка обмеження виводу GPIO46 (лише вхід)
    if (pin == GPIO_NUM_46 && (mode == GPIO_MODE_OUTPUT || mode == GPIO_MODE_INPUT_OUTPUT)) {
        ESP_LOGE(TAG, "Помилка: GPIO46 підтримує лише режим входу (input-only)!");
        return ESP_ERR_INVALID_ARG;
    }

    // Попередження при призначенні критичних завантажувальних виводів strapping
    if (pin == GPIO_NUM_0 || pin == GPIO_NUM_3 || pin == GPIO_NUM_45) {
        ESP_LOGW(TAG, "Увага: GPIO%d є strapping-виводом! Перевірте зовнішні підтяжки.", pin);
    }

    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << pin),
        .mode = mode,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };

    return gpio_config(&io_conf);
}
