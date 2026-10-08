#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define MINI360_EN_PIN GPIO_NUM_4

void power_node_init(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << MINI360_EN_PIN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
    // Активація перетворювача Mini360 подачею високого рівня
    gpio_set_level(MINI360_EN_PIN, 1);
}

void power_node_shutdown(void) {
    // Переведення MP1482 у режим глибокого сну
    gpio_set_level(MINI360_EN_PIN, 0);
}
