// Приклад ініціалізації та керування виводом nSLEEP для DRV8833 у C (ESP-IDF)
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

#define DRV8833_NSLEEP_GPIO  GPIO_NUM_18
#define DRV8833_AIN1_GPIO    GPIO_NUM_19
#define DRV8833_AIN2_GPIO    GPIO_NUM_21

void drv8833_init_hardware(void) {
    // Налаштування конфігурації GPIO виводу nSLEEP
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << DRV8833_NSLEEP_GPIO) | (1ULL << DRV8833_AIN1_GPIO) | (1ULL << DRV8833_AIN2_GPIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);

    // Початковий стан: сплячий режим (nSLEEP = 0)
    gpio_set_level(DRV8833_NSLEEP_GPIO, 0);
    gpio_set_level(DRV8833_AIN1_GPIO, 0);
    gpio_set_level(DRV8833_AIN2_GPIO, 0);
}

void drv8833_wake_up(void) {
    // Пробудження драйвера: переведення nSLEEP у високий рівень (1)
    gpio_set_level(DRV8833_NSLEEP_GPIO, 1);
    
    // Обов'язкова павза для заряду ємностей VCAP та VCP (помпи заряду)
    vTaskDelay(pdMS_TO_TICKS(2));
}
