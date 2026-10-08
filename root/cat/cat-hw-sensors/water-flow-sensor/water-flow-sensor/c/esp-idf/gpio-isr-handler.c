// Зчитування імпульсів витратоміра води в ESP-IDF з використанням GPIO EXTI
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

#define FLOW_SENSOR_GPIO GPIO_NUM_4
#define K_FACTOR 7.5f

static volatile uint32_t pulse_count = 0;

static void IRAM_ATTR gpio_isr_handler(void* arg) {
    pulse_count++;
}

void app_main(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << FLOW_SENSOR_GPIO),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_POSEDGE
    };
    gpio_config(&io_conf);

    gpio_install_isr_service(0);
    gpio_isr_handler_add(FLOW_SENSOR_GPIO, gpio_isr_handler, NULL);

    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));

        // Атомарне зчитування з тимчасовим вимкненням переривання лінії
        gpio_intr_disable(FLOW_SENSOR_GPIO);
        uint32_t pulses = pulse_count;
        pulse_count = 0;
        gpio_intr_enable(FLOW_SENSOR_GPIO);

        float flow_rate = (float)pulses / K_FACTOR;
        printf("Поточна витрата води: %.2f Л/хв\n", flow_rate);
    }
}
