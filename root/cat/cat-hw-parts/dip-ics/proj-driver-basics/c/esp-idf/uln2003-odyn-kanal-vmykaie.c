// ULN2003: клацаємо реле раз на секунду через канал 1.
// GPIO18 → IN1 (вивід 1 чипа). Реле: +5V → обмотка → OUT1 (вивід 16).
// COM (вивід 9) → +5V живлення реле — обов'язково, це вмикає гасильний діод.
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define RELAY_CH  GPIO_NUM_18     // нога МК, що керує входом каналу 1

void app_main(void) {
    gpio_config_t io = {
        .pin_bit_mask = 1ULL << RELAY_CH,
        .mode = GPIO_MODE_OUTPUT,
    };
    gpio_config(&io);             // те саме, що pinMode(): нога у вихід

    while (1) {
        gpio_set_level(RELAY_CH, 1);      // «1» на IN1 → OUT1 сідає на землю → реле спрацьовує
        vTaskDelay(pdMS_TO_TICKS(1000));
        gpio_set_level(RELAY_CH, 0);      // «0» → OUT1 відпускається → реле відпускає
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
