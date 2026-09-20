// C (ESP-IDF)
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define RELAY_GPIO GPIO_NUM_0

void app_main(void) {
    // Попередньо виставляємо логічну одиницю на виводі для вимкненого стану реле
    gpio_set_level(RELAY_GPIO, 1);

    // Конфігуруємо напрямок виводу GPIO0 на вихід
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << RELAY_GPIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);

    while (1) {
        // Увімкнення реле (активний низький рівень)
        gpio_set_level(RELAY_GPIO, 0);
        vTaskDelay(pdMS_TO_TICKS(1000));

        // Вимкнення реле (високий рівень)
        gpio_set_level(RELAY_GPIO, 1);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
