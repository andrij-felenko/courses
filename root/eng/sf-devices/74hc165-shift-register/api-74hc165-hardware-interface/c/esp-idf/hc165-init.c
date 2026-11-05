#include "driver/gpio.h"
#include "rom/ets_sys.h"

#define PIN_PL 18
#define PIN_CP 19
#define PIN_Q7 21

void hc165_init() {
    gpio_set_direction(PIN_PL, GPIO_MODE_OUTPUT);
    gpio_set_direction(PIN_CP, GPIO_MODE_OUTPUT);
    gpio_set_direction(PIN_Q7, GPIO_MODE_INPUT);
    
    gpio_set_level(PIN_PL, 1);
    gpio_set_level(PIN_CP, 0);
}

uint8_t hc165_read() {
    uint8_t data = 0;
    
    // Захоплення даних
    gpio_set_level(PIN_PL, 0);
    ets_delay_us(1);
    gpio_set_level(PIN_PL, 1);
    ets_delay_us(1);
    
    // Читання 8 бітів
    for (int i = 0; i < 8; i++) {
        // Читаємо поточний біт з Q7
        int bit = gpio_get_level(PIN_Q7);
        data |= (bit << (7 - i));
        
        // Зсув до наступного біта
        gpio_set_level(PIN_CP, 1);
        ets_delay_us(1);
        gpio_set_level(PIN_CP, 0);
        ets_delay_us(1);
    }
    
    return data;
}
