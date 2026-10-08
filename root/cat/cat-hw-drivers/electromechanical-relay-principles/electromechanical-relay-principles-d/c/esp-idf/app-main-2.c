// Приклад керування силовим реле в середовищі ESP-IDF (C)
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define RELAY_GPIO_PIN GPIO_NUM_4

void app_main(void) {
    // Конфігурація виводу GPIO як виходу зі стягувальним резистором
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << RELAY_GPIO_PIN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);

    while (1) {
        // Подача сигналу на силовий ключ
        gpio_set_level(RELAY_GPIO_PIN, 1);
        vTaskDelay(pdMS_TO_TICKS(20)); // Очікування механічної стабілізації контактів

        vTaskDelay(pdMS_TO_TICKS(5000));

        // Зняття сигналу керування
        gpio_set_level(RELAY_GPIO_PIN, 0);
        vTaskDelay(pdMS_TO_TICKS(20)); // Очікування розмикання якоря та гасіння сплеску ЕРС

        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}
