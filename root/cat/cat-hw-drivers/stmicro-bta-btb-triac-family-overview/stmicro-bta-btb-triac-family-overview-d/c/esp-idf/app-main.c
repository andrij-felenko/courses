#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// Призначення піна керування світлодіодом оптосимістора
#define TRIAC_CTRL_PIN  GPIO_NUM_18

void app_main(void)
{
    // Налаштування конфігурації GPIO
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << TRIAC_CTRL_PIN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);

    while (1) {
        // Увімкнення навантаження (оптосимістор з детектором нуля чекає 0 В)
        gpio_set_level(TRIAC_CTRL_PIN, 1);
        vTaskDelay(pdMS_TO_TICKS(5000));

        // Вимкнення навантаження
        gpio_set_level(TRIAC_CTRL_PIN, 0);
        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}
