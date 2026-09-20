#include "driver/gpio.h"
#include "rom/ets_sys.h"

#define PIN_PL  GPIO_NUM_4
#define PIN_CP  GPIO_NUM_5
#define PIN_Q7  GPIO_NUM_18

uint16_t read_dip_switches_cascade(void) {
    uint16_t data = 0;
    
    // Засувка станів DIP-перемикачів
    gpio_set_level(PIN_PL, 0);
    ets_delay_us(1);
    gpio_set_level(PIN_PL, 1);
    
    // Послідовне зчитування 16 бітів
    for (int i = 0; i < 16; i++) {
        data <<= 1;
        if (gpio_get_level(PIN_Q7)) {
            data |= 0x0001;
        }
        gpio_set_level(PIN_CP, 1);
        ets_delay_us(1);
        gpio_set_level(PIN_CP, 0);
        ets_delay_us(1);
    }
    return data;
}
