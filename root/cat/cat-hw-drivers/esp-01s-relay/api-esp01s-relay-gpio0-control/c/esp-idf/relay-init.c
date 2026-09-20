#include "driver/gpio.h"

#define RELAY_GPIO GPIO_NUM_0

void relay_init(void) {
    // Спочатку записуємо високий рівень у регістр виходу
    gpio_set_level(RELAY_GPIO, 1);
    
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << RELAY_GPIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
}

void relay_set_state(bool enable) {
    // Інверсна логіка: 0 вмикає реле, 1 вимикає
    gpio_set_level(RELAY_GPIO, enable ? 0 : 1);
}
