#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define TRIAC_GATE_GPIO  GPIO_NUM_18

void init_triac_gate(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << TRIAC_GATE_GPIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
    gpio_set_level(TRIAC_GATE_GPIO, 0);
}

void trigger_triac_pulse(uint32_t pulse_us) {
    // Подача позитивного імпульсу на світлодіод оптосимістора
    gpio_set_level(TRIAC_GATE_GPIO, 1);
    ets_delay_us(pulse_us); // Короткий тригерний імпульс (наприклад, 50 мкс)
    gpio_set_level(TRIAC_GATE_GPIO, 0);
}
