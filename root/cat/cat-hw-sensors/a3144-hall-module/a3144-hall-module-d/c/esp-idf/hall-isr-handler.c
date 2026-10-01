#include "driver/gpio.h"

#define HALL_SENSOR_PIN GPIO_NUM_4

static volatile uint32_t pulse_count = 0;

static void IRAM_ATTR hall_isr_handler(void* arg) {
    pulse_count++;
}

void init_hall_sensor(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << HALL_SENSOR_PIN),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .intr_type = GPIO_INTR_NEGEDGE
    };
    gpio_config(&io_conf);
    gpio_isr_handler_add(HALL_SENSOR_PIN, hall_isr_handler, NULL);
}
