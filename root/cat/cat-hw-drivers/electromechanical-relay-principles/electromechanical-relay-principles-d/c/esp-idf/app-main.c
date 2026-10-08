#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define RELAY_PIN GPIO_NUM_18

void app_main(void) {
    // Налаштування GPIO виводу для керування транзисторним ключем реле
    gpio_reset_pin(RELAY_PIN);
    gpio_set_direction(RELAY_PIN, GPIO_MODE_OUTPUT);

    while (1) {
        // Увімкнення реле (подача високого рівня на затвор/базу)
        gpio_set_level(RELAY_PIN, 1);
        vTaskDelay(pdMS_TO_TICKS(2000)); // Утримання 2 секунди

        // Вимкнення реле та очікування завершення перехідного процесу
        gpio_set_level(RELAY_PIN, 0);
        vTaskDelay(pdMS_TO_TICKS(2000)); // Пауза для безпечного охолодження контактів
    }
}
