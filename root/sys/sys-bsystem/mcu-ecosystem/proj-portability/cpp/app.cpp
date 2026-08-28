// app.cpp — прикладна логіка; не інклудить Arduino.h, IDF, avr/io.h
#include "hal.h"

#define LED_PIN 2   // номер ніжки: оголошено у board_config.h або тут

void app_main(void) {
    hal_gpio_write(LED_PIN, false);   // старт — LED вимкнено
    for (;;) {
        hal_gpio_write(LED_PIN, true);
        hal_delay_ms(200);
        hal_gpio_write(LED_PIN, false);
        hal_delay_ms(200);
        hal_uart_puts("tick\n");
    }
}
