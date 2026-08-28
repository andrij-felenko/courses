/* Налаштування сили вихідного каскаду в ESP-IDF (ESP32)
 * Зниження струмової здатності сповільнює dV/dt та di/dt,
 * радикально пригнічуючи Ground Bounce та дзвін. */

#include "driver/gpio.h"

gpio_config_t io_conf = {
    .pin_bit_mask = (1ULL << GPIO_NUM_18), // SPI CLK
    .mode = GPIO_MODE_OUTPUT,
    .pull_up_en = GPIO_PULLUP_DISABLE,
    .pull_down_en = GPIO_PULLDOWN_DISABLE,
    .intr_type = GPIO_INTR_DISABLE
};
gpio_config(&io_conf);

/* Доступні рівні:
 * GPIO_DRIVE_CAP_0 : слабкий (~5 мА, найм'якший фронт)
 * GPIO_DRIVE_CAP_1 : середній (~10 мА)
 * GPIO_DRIVE_CAP_2 : стандартний (~20 мА)
 * GPIO_DRIVE_CAP_3 : максимальний (~40 мА, максимальний шум) */
gpio_set_drive_capability(GPIO_NUM_18, GPIO_DRIVE_CAP_1);
