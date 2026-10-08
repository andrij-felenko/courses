#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define KEEP_ALIVE_GPIO GPIO_NUM_18

void ip5310_keep_alive_task(void *pvParameters) {
    gpio_reset_pin(KEEP_ALIVE_GPIO);
    gpio_set_direction(KEEP_ALIVE_GPIO, GPIO_MODE_OUTPUT);

    while (1) {
        // Затримка 15 секунд перед наступним імпульсом
        vTaskDelay(pdMS_TO_TICKS(15000));

        // Генерація струмового імпульсу ~150 мА протягом 150 мс
        gpio_set_level(KEEP_ALIVE_GPIO, 1);
        vTaskDelay(pdMS_TO_TICKS(150));
        gpio_set_level(KEEP_ALIVE_GPIO, 0);
    }
}
