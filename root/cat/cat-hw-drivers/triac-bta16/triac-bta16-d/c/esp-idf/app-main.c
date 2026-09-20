// Керування силовим симістором BTA16-600B в середовищі ESP-IDF
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define TRIAC_GATE_GPIO GPIO_NUM_18

void app_main(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << TRIAC_GATE_GPIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);

    while (1) {
        // Подача сигналу відмикання на оптосимістор
        gpio_set_level(TRIAC_GATE_GPIO, 1);
        vTaskDelay(pdMS_TO_TICKS(5000));

        // Зняття сигналу керування
        gpio_set_level(TRIAC_GATE_GPIO, 0);
        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}
