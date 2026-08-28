#include "driver/gpio.h"

#define PIN_DIN   GPIO_NUM_23   // дані в MAX7219
#define PIN_CLK   GPIO_NUM_18   // такт
#define PIN_LOAD  GPIO_NUM_5    // завантаження (CS)

// Надіслати один 16-бітний кадр: адреса реєстра + байт даних.
static void max7219send(uint8_t addr, uint8_t data) {
    uint16_t frame16 = ((uint16_t)addr << 8) | data;   // старший байт = адреса
    gpio_set_level(PIN_LOAD, 0);                        // почали кадр
    for (int i = 15; i >= 0; i--) {                     // старшим бітом уперед
        gpio_set_level(PIN_CLK, 0);
        gpio_set_level(PIN_DIN, (frame16 >> i) & 1);    // виставити біт
        gpio_set_level(PIN_CLK, 1);                     // фронт CLK → чип зчитав біт
    }
    gpio_set_level(PIN_LOAD, 1);                        // фронт LOAD → клацнути в реєстр
}
