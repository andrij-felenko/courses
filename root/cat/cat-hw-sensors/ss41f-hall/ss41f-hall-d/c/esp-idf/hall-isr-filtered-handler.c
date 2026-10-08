#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_timer.h"

#define HALL_GPIO GPIO_NUM_4
#define MIN_PULSE_INTERVAL_US 500  // Мінімальний інтервал між імпульсами (500 мкс)

static volatile uint32_t valid_pulse_count = 0;
static volatile int64_t last_interrupt_time = 0;

static void IRAM_ATTR hall_isr_filtered_handler(void* arg) {
    int64_t current_time = esp_timer_get_time();
    if ((current_time - last_interrupt_time) >= MIN_PULSE_INTERVAL_US) {
        valid_pulse_count++;
        last_interrupt_time = current_time;
    }
}

void app_main(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << HALL_GPIO),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_ANYEDGE
    };
    gpio_config(&io_conf);

    gpio_install_isr_service(0);
    gpio_isr_handler_add(HALL_GPIO, hall_isr_filtered_handler, NULL);

    while (1) {
        printf("Відфільтрована кількість імпульсів: %lu\n", (unsigned long)valid_pulse_count);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
