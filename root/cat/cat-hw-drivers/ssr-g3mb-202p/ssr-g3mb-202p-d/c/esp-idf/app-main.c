#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define SSR_CONTROL_PIN GPIO_NUM_4

void app_main(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << SSR_CONTROL_PIN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);

    while (1) {
        // Увімкнення навантаження 230 В
        gpio_set_level(SSR_CONTROL_PIN, 1);
        vTaskDelay(pdMS_TO_TICKS(5000));

        // Вимкнення навантаження
        gpio_set_level(SSR_CONTROL_PIN, 0);
        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}
