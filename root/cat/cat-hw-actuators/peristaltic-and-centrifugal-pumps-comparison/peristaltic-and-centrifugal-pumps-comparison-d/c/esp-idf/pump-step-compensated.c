// Ідіоматична реалізація компенсації на ESP-IDF через GPIO таймер
#include "driver/gpio.h"
#include "rom/ets_sys.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define STEP_GPIO GPIO_NUM_18
#define DIR_GPIO  GPIO_NUM_19
#define ROLLERS_COUNT 3
#define STEPS_PER_REV 200

void pump_step_compensated(uint32_t step_index) {
    uint32_t steps_per_roller = STEPS_PER_REV / ROLLERS_COUNT;
    uint32_t phase = step_index % steps_per_roller;
    uint32_t delay_us = 1000;

    if (phase > (steps_per_roller * 9 / 10)) {
        delay_us = 400; // Зменшення паузи при відриві ролика
    }

    gpio_set_level(STEP_GPIO, 1);
    ets_delay_us(10);
    gpio_set_level(STEP_GPIO, 0);
    ets_delay_us(delay_us);
}
