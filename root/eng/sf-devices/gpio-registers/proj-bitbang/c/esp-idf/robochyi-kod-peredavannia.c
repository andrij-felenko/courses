#include "driver/gpio.h"

#define PIN_DATA  GPIO_NUM_23
#define PIN_CLK   GPIO_NUM_18

void send_byte_slow(uint8_t b) {        // старший біт першим
    for (int i = 7; i >= 0; i--) {
        gpio_set_level(PIN_DATA, (b >> i) & 1);  // виставити поточний біт
        gpio_set_level(PIN_CLK, 1);              // наростальний фронт — приймач читає
        gpio_set_level(PIN_CLK, 0);
    }
}
