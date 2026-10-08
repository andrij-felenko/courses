#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_timer.h"

#define SENSOR_GPIO GPIO_NUM_4
#define K_FACTOR 7.5f

static volatile uint32_t pulse_count = 0;

static void IRAM_ATTR gpio_isr_handler(void* arg) {
    pulse_count++;
}

void app_main(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << SENSOR_GPIO),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_NEGEDGE
    };
    gpio_config(&io_conf);

    gpio_install_isr_service(0);
    gpio_isr_handler_add(SENSOR_GPIO, gpio_isr_handler, NULL);

    uint32_t last_count = 0;
    int64_t last_time = esp_timer_get_time();

    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
        
        int64_t now = esp_timer_get_time();
        uint32_t current_count;

        gpio_intr_disable(SENSOR_GPIO);
        current_count = pulse_count;
        gpio_intr_enable(SENSOR_GPIO);

        uint32_t pulses = current_count - last_count;
        double dt = (now - last_time) / 1000000.0;
        
        double frequency = pulses / dt;
        double flow_rate = frequency / K_FACTOR;

        last_count = current_count;
        last_time = now;

        printf("Частота: %.1f Гц | Витрата: %.2f Л/хв\n", frequency, flow_rate);
    }
}
