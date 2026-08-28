#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define MOTOR_PIN GPIO_NUM_5       // GPIO → Rb → база NPN-ключа

void motor_task(void *arg) {
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << MOTOR_PIN,
        .mode         = GPIO_MODE_OUTPUT,
    };
    ESP_ERROR_CHECK(gpio_config(&cfg));
    gpio_set_level(MOTOR_PIN, 0);       // старт: транзистор закритий, мотор стоїть

    for (;;) {
        gpio_set_level(MOTOR_PIN, 1);   // «1» → база відкрита → мотор крутиться
        vTaskDelay(pdMS_TO_TICKS(2000));
        gpio_set_level(MOTOR_PIN, 0);   // «0» → база закрита → мотор стоїть
        vTaskDelay(pdMS_TO_TICKS(2000));
    }
}
