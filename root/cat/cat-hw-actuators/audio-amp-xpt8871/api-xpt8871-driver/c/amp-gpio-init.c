// Безпечна ініціалізація лінії SHDN у середовищі ESP-IDF
#include "driver/gpio.h"

#define PIN_AMP_SHDN GPIO_NUM_4

esp_err_t amp_gpio_init(void) {
    // 1. Спочатку скидаємо вихідний рівень у нуль
    gpio_set_level(PIN_AMP_SHDN, 0);

    // 2. Налаштовуємо режим push-pull з апаратним pull-down
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << PIN_AMP_SHDN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    return gpio_config(&io_conf);
}
