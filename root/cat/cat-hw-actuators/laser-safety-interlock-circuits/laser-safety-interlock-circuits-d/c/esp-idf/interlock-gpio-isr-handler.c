// Програмний моніторинг апаратного інтерлоку (ESP-IDF C)
// Забезпечує пасивну діагностику та контроль гальванічно розв'язаного сигналу зворотного зв'язку.

#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

#define INTERLOCK_FB_GPIO   GPIO_NUM_4
#define LASER_ENABLE_GPIO   GPIO_NUM_5
#define STATUS_LED_GPIO     GPIO_NUM_18

static volatile bool s_interlock_active = false;

static void IRAM_ATTR interlock_gpio_isr_handler(void* arg) {
    int level = gpio_get_level(INTERLOCK_FB_GPIO);
    s_interlock_active = (level == 1);
}

void app_main(void) {
    // Налаштування входу моніторингу інтерлоку
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << INTERLOCK_FB_GPIO),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_ANYEDGE
    };
    gpio_config(&io_conf);

    // Налаштування виходів програмного дозволу та індикації
    io_conf.pin_bit_mask = (1ULL << LASER_ENABLE_GPIO) | (1ULL << STATUS_LED_GPIO);
    io_conf.mode = GPIO_MODE_OUTPUT;
    io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    io_conf.intr_type = GPIO_INTR_DISABLE;
    gpio_config(&io_conf);

    // Початковий стан — вимкнено
    gpio_set_level(LASER_ENABLE_GPIO, 0);
    gpio_set_level(STATUS_LED_GPIO, 0);

    // Встановлення обробника переривань
    gpio_install_isr_service(0);
    gpio_isr_handler_add(INTERLOCK_FB_GPIO, interlock_gpio_isr_handler, NULL);

    s_interlock_active = (gpio_get_level(INTERLOCK_FB_GPIO) == 1);

    while (1) {
        if (s_interlock_active) {
            gpio_set_level(STATUS_LED_GPIO, 1);
            gpio_set_level(LASER_ENABLE_GPIO, 1);
        } else {
            gpio_set_level(STATUS_LED_GPIO, 0);
            gpio_set_level(LASER_ENABLE_GPIO, 0);
        }
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
