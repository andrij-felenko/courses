#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_LED  GPIO_NUM_18     // ніжка OUT зі схеми — до неї резистор і світлодіод

void app_main(void) {
    gpio_config_t out = {
        .pin_bit_mask = 1ULL << PIN_LED,
        .mode = GPIO_MODE_OUTPUT,
    };
    gpio_config(&out);           // те саме оголошення: ніжка — вихід, тепер вона НАВ'ЯЗУЄ напругу

    while (1) {
        gpio_set_level(PIN_LED, 1);      // ніжка тягне до живлення → тече струм → LED світиться
        vTaskDelay(pdMS_TO_TICKS(500));  // тримаємо так 500 мс
        gpio_set_level(PIN_LED, 0);      // ніжка тягне до нуля → різниці напруг нема → LED гасне
        vTaskDelay(pdMS_TO_TICKS(500));  // тримаємо темряву 500 мс
    }
}
