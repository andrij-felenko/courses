// Керування апаратним напівпровідниковим тригером блокування (ESP-IDF C)
// Забезпечує безпечне формування імпульсу повторної ініціалізації RS-тригера.

#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

#define LATCH_STATUS_GPIO   GPIO_NUM_16
#define INTERLOCK_OK_GPIO   GPIO_NUM_17
#define HW_RESET_TRIG_GPIO  GPIO_NUM_18

bool try_hardware_reset(void) {
    if (gpio_get_level(INTERLOCK_OK_GPIO) == 1) {
        gpio_set_level(HW_RESET_TRIG_GPIO, 1);
        vTaskDelay(pdMS_TO_TICKS(50));
        gpio_set_level(HW_RESET_TRIG_GPIO, 0);
        
        vTaskDelay(pdMS_TO_TICKS(10));
        return (gpio_get_level(LATCH_STATUS_GPIO) == 1);
    }
    return false;
}

void app_main(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << LATCH_STATUS_GPIO) | (1ULL << INTERLOCK_OK_GPIO),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);

    io_conf.pin_bit_mask = (1ULL << HW_RESET_TRIG_GPIO);
    io_conf.mode = GPIO_MODE_OUTPUT;
    gpio_config(&io_conf);

    gpio_set_level(HW_RESET_TRIG_GPIO, 0);

    while (1) {
        int latch_status = gpio_get_level(LATCH_STATUS_GPIO);
        if (latch_status == 0) {
            try_hardware_reset();
        }
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
