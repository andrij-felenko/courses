#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define LASER GPIO_NUM_18      // пін S модуля -> GPIO18

void app_main(void)
{
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << LASER,
        .mode         = GPIO_MODE_OUTPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    gpio_config(&cfg);
    gpio_set_level(LASER, 0);   // старт з вимкненим променем — гарна звичка

    while (1) {
        gpio_set_level(LASER, 1);            // промінь увімкнено
        vTaskDelay(pdMS_TO_TICKS(1000));
        gpio_set_level(LASER, 0);            // промінь вимкнено
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
