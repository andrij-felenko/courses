#include "driver/gpio.h"

static const gpio_num_t PINS[4] = {GPIO_NUM_16, GPIO_NUM_17, GPIO_NUM_18, GPIO_NUM_19};

void hal_esp_high(uint8_t pin) {
    gpio_num_t p = PINS[pin];
    gpio_set_direction(p, GPIO_MODE_OUTPUT);
    gpio_set_level(p, 1);
}

void hal_esp_low(uint8_t pin) {
    gpio_num_t p = PINS[pin];
    gpio_set_direction(p, GPIO_MODE_OUTPUT);
    gpio_set_level(p, 0);
}

void hal_esp_hiz(uint8_t pin) {
    gpio_num_t p = PINS[pin];
    gpio_set_direction(p, GPIO_MODE_INPUT);
    gpio_set_pull_mode(p, GPIO_FLOATING);
}
