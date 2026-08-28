#include "driver/gpio.h"
// вихід компаратора на GPIO4; підтяжку на платі ведемо до 3.3 В (вигода №1)
gpio_config_t io = {
    .pin_bit_mask = 1ULL << GPIO_NUM_4,
    .mode         = GPIO_MODE_INPUT,
    .pull_up_en   = GPIO_PULLUP_DISABLE,   // «1» дає зовнішній Rpull
    .pull_down_en = GPIO_PULLDOWN_DISABLE,
    .intr_type    = GPIO_INTR_DISABLE,
};
ESP_ERROR_CHECK(gpio_config(&io));

if (gpio_get_level(GPIO_NUM_4)) {          // вихід відпущений → перейдено поріг
    fan_on();                              // гаряче: вмикаємо вентилятор
} else {
    fan_off();                             // холодно
}
