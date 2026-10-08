#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

#define HALL_SENSOR_GPIO GPIO_NUM_4

static volatile uint32_t pulse_count = 0;

static void IRAM_ATTR hall_sensor_isr_handler(void* arg) {
    pulse_count++;
}

void app_main(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << HALL_SENSOR_GPIO),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_ANYEDGE
    };
    gpio_config(&io_conf);

    gpio_install_isr_service(0);
    gpio_isr_handler_add(HALL_SENSOR_GPIO, hall_sensor_isr_handler, NULL);

    while (1) {
        printf("Кількість перемикань полюсів: %lu\n", (unsigned long)pulse_count);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
