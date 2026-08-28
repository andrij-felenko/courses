#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define LED_GPIO GPIO_NUM_2          // світлодіод на платі (звір із розводкою!)

void app_main(void) {
    gpio_reset_pin(LED_GPIO);                       // вивід у відомий стан
    gpio_set_direction(LED_GPIO, GPIO_MODE_OUTPUT); // тепер це вихід

    while (1) {                                     // "серцебиття": видимий пульс життя
        gpio_set_level(LED_GPIO, 1);                // світлодіод увімкнено
        vTaskDelay(pdMS_TO_TICKS(500));             // пауза 500 мс
        gpio_set_level(LED_GPIO, 0);                // світлодіод вимкнено
        vTaskDelay(pdMS_TO_TICKS(500));             // пауза 500 мс
    }
}
