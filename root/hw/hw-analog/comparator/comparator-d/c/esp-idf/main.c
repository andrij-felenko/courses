#include "driver/gpio.h"

// ніжку під вихід компаратора налаштовуємо один раз
gpio_config_t cfg = {
    .pin_bit_mask = 1ULL << LIGHT_GPIO,
    .mode         = GPIO_MODE_INPUT,
    .pull_up_en   = GPIO_PULLUP_DISABLE,    // підтяжка вже є зовні (відкритий колектор)
    .pull_down_en = GPIO_PULLDOWN_DISABLE,
    .intr_type    = GPIO_INTR_DISABLE,
};
ESP_ERROR_CHECK(gpio_config(&cfg));

if (gpio_get_level(LIGHT_GPIO)) {           // напруга нижче порога → стемніло
    lamp_on();
} else {                                    // вище порога → ще видно
    lamp_off();
}
