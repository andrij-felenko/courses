#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"

#define REED_PIN GPIO_NUM_4

void app_main(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << REED_PIN),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
}
