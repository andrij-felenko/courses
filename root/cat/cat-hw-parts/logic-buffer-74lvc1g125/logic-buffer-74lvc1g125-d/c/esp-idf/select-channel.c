// C / ESP-IDF: Безпечне перемикання двоканального мультиплексора на 74LVC1G125
#include "driver/gpio.h"
#include "rom/ets_sys.h"

#define PIN_OE0  GPIO_NUM_4
#define PIN_OE1  GPIO_NUM_5

void select_channel(uint8_t channel) {
    if (channel == 0) {
        // Спочатку вимикаємо канал 1 у стан Hi-Z (break-before-make)
        gpio_set_level(PIN_OE1, 1);
        ets_delay_us(1); // Затримка для перекриття часових інтервалів
        gpio_set_level(PIN_OE0, 0);
    } else {
        // Спочатку вимикаємо канал 0 у стан Hi-Z
        gpio_set_level(PIN_OE0, 1);
        ets_delay_us(1);
        gpio_set_level(PIN_OE1, 0);
    }
}
