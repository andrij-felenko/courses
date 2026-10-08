// Приклад безшумного увімкнення підсилювача PAM8403 в ESP-IDF
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_SHDN GPIO_NUM_4
#define PIN_MUTE GPIO_NUM_5

void app_main(void) {
    // Конфігурація виводів GPIO
    gpio_reset_pin(PIN_SHDN);
    gpio_reset_pin(PIN_MUTE);
    gpio_set_direction(PIN_SHDN, GPIO_MODE_OUTPUT);
    gpio_set_direction(PIN_MUTE, GPIO_MODE_OUTPUT);

    // Початкове блокування підсилювача
    gpio_set_level(PIN_SHDN, 0);
    gpio_set_level(PIN_MUTE, 0);

    // Затримка для стабілізації живлення
    vTaskDelay(pdMS_TO_TICKS(100));

    // Активація внутрішніх кіл зсуву
    gpio_set_level(PIN_SHDN, 1);
    vTaskDelay(pdMS_TO_TICKS(50));

    // Увімкнення звукового тракту
    gpio_set_level(PIN_MUTE, 1);
}
