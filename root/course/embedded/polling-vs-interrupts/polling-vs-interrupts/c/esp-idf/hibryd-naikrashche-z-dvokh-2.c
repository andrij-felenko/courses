#include "driver/gpio.h"

#define SENSOR_PIN GPIO_NUM_4

volatile uint32_t turns = 0;           // спільне з ISR → volatile

static void IRAM_ATTR count_pulse(void *arg) {   // ISR: коротка, лише ++
    turns++;
}

void app_main(void) {
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << SENSOR_PIN,
        .mode = GPIO_MODE_INPUT,
        .intr_type = GPIO_INTR_POSEDGE,          // висхідний фронт
    };
    gpio_config(&cfg);

    gpio_install_isr_service(0);
    gpio_isr_handler_add(SENSOR_PIN, count_pulse, NULL);
    // ... задача вільна для решти роботи; залізо рахує саме ...
}
